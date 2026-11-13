include(joinpath(@__DIR__,"initialize_frozen.jl"))
BLAS.set_num_threads(1)
const OUT=joinpath(@__DIR__,"predictions");mkpath(OUT)
const CFG=JSON.parsefile(joinpath(@__DIR__,"protocol.json"))
nw,s0=initialize_frozen()
const FD=NetworkDynamics.ForwardDiff
const U0=copy(uflat(s0));const P0=copy(pflat(s0))
mass=diag(Matrix(linearize_network(s0).M))
const DX=findall(!iszero,mass);const AZ=findall(iszero,mass)
const MD=Diagonal(mass[DX]);const N=length(DX)
const VG=SII.getsym(nw,[VIndex(b,Symbol("busbar₊u_",part)) for b in 1:39 for part in ("r","i")])
residual(u,p)=begin r=zeros(promote_type(eltype(u),eltype(p)),length(u));nw(r,u,p,0.);r end
voltage(u,p)=collect(VG(NWState(nw,u,p,0.)))
const VH=FD.jacobian(uu->voltage(uu,P0),U0)

function consistent(x,p,seed=U0)
    u=copy(seed);u[DX]=x
    for it in 1:30
        r=residual(u,p)[AZ]
        if maximum(abs,r)<1e-11;return u;end
        J=FD.jacobian(z->begin uu=eltype(z).(u);uu[AZ]=z;residual(uu,p)[AZ] end,u[AZ])
        step=J\r
        # Damped Newton on the algebraic chart; no dynamic-state correction.
        accepted=false
        for alpha in (1.,.5,.25,.125,.0625,.03125)
            candidate=copy(u);candidate[AZ]-=alpha*step
            if norm(residual(candidate,p)[AZ])<norm(r)
                u=candidate;accepted=true;break
            end
        end
        @assert accepted "Algebraic Newton stalled"
    end
    error("Algebraic Newton did not converge")
end

function local_model(x,p)
    u=consistent(x,p)
    J=FD.jacobian(uu->residual(uu,p),u)
    Z=-(J[AZ,AZ]\J[AZ,DX])
    A=MD\(J[DX,DX]+J[DX,AZ]*Z)
    C=VH[:,DX]+VH[:,AZ]*Z
    f=MD\residual(u,p)[DX]
    u,A,C,f
end

function advance(A,b)
    aug=zeros(N+1,N+1);aug[1:N,1:N]=A;aug[1:N,N+1]=b
    exp(aug/CFG["report_hz"])
end

function parameters(case,t)
    p=copy(P0)
    if case["on"]<=t<case["off"]
        if case["kind"]=="line"
            p[SII.parameter_index(nw,EIndex(case["edge"],:piline₊active))]=0.
        else
            for sym in (:ZIPLoad₊Pset,:ZIPLoad₊Qset)
                i=SII.parameter_index(nw,VIndex(case["bus"],sym));p[i]*=case["factor"]
            end
        end
    end
    p
end

function writevolt(name,t,v)
    CSV.write(joinpath(OUT,name*".csv"),hcat(DataFrame(time_s=t),DataFrame(v,[Symbol("V",b,"_",part) for b in 1:39 for part in ("r","i")])))
end

function fixed_predict(case,times)
    # Same fixed-reference affine physical predictor as descriptor_bridge.
    u0,A0,C0,f0=local_model(U0[DX],P0)
    p1=case["kind"]=="line" ? parameters(case,case["on"]) : copy(P0)
    u1,A1,C1,f1=local_model(U0[DX],p1)
    D=zeros(78);B=zeros(N)
    if case["kind"]=="load"
        ip=[SII.parameter_index(nw,VIndex(case["bus"],sym)) for sym in (:ZIPLoad₊Pset,:ZIPLoad₊Qset)]
        par(a)=begin pp=eltype(a).(P0);pp[ip].=P0[ip].*(1+a[1]);pp end
        J=FD.jacobian(uu->residual(uu,P0),u0)
        Ju=FD.jacobian(a->residual(u0,par(a)),[0.])
        Zu=-(J[AZ,AZ]\Ju[AZ,:])
        B=vec(MD\(Ju[DX,:]+J[DX,AZ]*Zu));D=vec(VH[:,AZ]*Zu)
    end
    amp=case["kind"]=="load" ? case["factor"]-1 : 0.
    E0=advance(A0,f0);E1=advance(A1,f1+B*amp)
    x=zeros(N);v=zeros(length(times),78);base=copy(v);nonlinear=copy(v);maxalg=0.
    for (k,t) in enumerate(times)
        active=case["on"]<=t<case["off"]
        anchor=active ? u1 : u0;C=active ? C1 : C0;p=parameters(case,t)
        base[k,:]=voltage(anchor,p);v[k,:]=base[k,:]+C*x+(active ? D*amp : zero(D))
        u=consistent(U0[DX]+x,p);nonlinear[k,:]=voltage(u,p)
        maxalg=max(maxalg,maximum(abs,residual(u,p)[AZ]))
        x=((active ? E1 : E0)*vcat(x,1.))[1:N]
    end
    writevolt(case["id"]*"_fixed_complex",times,v)
    writevolt(case["id"]*"_fixed_base",times,base)
    writevolt(case["id"]*"_fixed_nonlinear_observation",times,nonlinear)
    maxalg
end

function recentered_predict(case,times,refresh)
    x=copy(U0[DX]);anchor=copy(x);v=zeros(length(times),78);elapsed=zeros(length(times))
    E=Matrix{Float64}(I,N+1,N+1);previous_active=false;last_refresh=1
    maxalg=0.;jump=0.;refreshes=0
    for (k,t) in enumerate(times)
        start=time_ns();active=case["on"]<=t<case["off"];p=parameters(case,t)
        if k==1 || active!=previous_active || k-last_refresh>=refresh
            before=copy(x)
            u,A,C,f=local_model(x,p);anchor=copy(x);E=advance(A,f)
            jump=max(jump,maximum(abs,x-before))
            last_refresh=k;refreshes+=1
        end
        u=consistent(x,p);v[k,:]=voltage(u,p)
        maxalg=max(maxalg,maximum(abs,residual(u,p)[AZ]))
        if k<length(times);x=anchor+(E*vcat(x-anchor,1.))[1:N];end
        previous_active=active;elapsed[k]=(time_ns()-start)/1e9
    end
    writevolt(case["id"]*"_relinearized_"*string(refresh),times,v)
    CSV.write(joinpath(OUT,case["id"]*"_timing_"*string(refresh)*".csv"),DataFrame(time_s=times,seconds=elapsed))
    Dict("algebraic_residual"=>maxalg,"recenter_state_jump"=>jump,"refreshes"=>refreshes,"elapsed_s"=>sum(elapsed))
end

function run_all()
    times=collect(0:1/CFG["report_hz"]:CFG["duration_s"])
    statuses=[]
    for case in CFG["cases"]
        println("PREDICT ",case["id"]);flush(stdout)
        row=Dict{String,Any}("case"=>case["id"])
        try
            row["fixed_observation_algebraic_residual"]=fixed_predict(case,times)
            for refresh in [CFG["refresh_reports"],CFG["convergence_refresh_reports"]]
                row["relinearized_"*string(refresh)]=recentered_predict(case,times,refresh)
            end
            row["status"]="SUCCESS"
        catch e
            row["status"]="FAILED";row["error"]=sprint(showerror,e,catch_backtrace())
        end
        push!(statuses,row);jsonwrite(joinpath(OUT,"STATUS.json"),statuses)
        println(JSON.json(row));flush(stdout)
    end
end
run_all()
