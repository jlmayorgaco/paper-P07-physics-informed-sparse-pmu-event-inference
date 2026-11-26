function extract_operators(nw,s0)
    FD=NetworkDynamics.ForwardDiff
    u0=copy(uflat(s0));p0=copy(pflat(s0));desc=linearize_network(s0)
    M=Matrix(desc.M);@assert isdiag(M)
    mass=diag(M);dyn=findall(!iszero,mass);alg=findall(iszero,mass)
    @assert length(dyn)==114 && length(alg)==78
    Md=M[dyn,dyn]
    dest=joinpath(DEST,"operators");mkpath(dest)
    writearray(dir,name,x)=CSV.write(joinpath(dir,name*".csv"),DataFrame(reshape(x,size(x,1),:),:auto))
    writearray(dest,"M",M)
    CSV.write(joinpath(dest,"state_index.csv"),DataFrame(index=1:length(u0),symbol=string.(SII.variable_symbols(nw)),mass=mass))
    residual(u,p)=begin r=zeros(promote_type(eltype(u),eltype(p)),length(u));nw(r,u,p,0.0);r end
    vg=SII.getsym(nw,[VIndex(b,Symbol("busbar₊u_",part)) for b in 1:39 for part in ("r","i")])
    volt(u,p)=collect(vg(NWState(nw,u,p,0.0)))
    function consistent(x,p)
        local u=copy(u0);u[dyn]=x
        for it in 1:30
            local r=residual(u,p)[alg];maximum(abs,r)<1e-12 && break
            local J=FD.jacobian(z->begin uu=eltype(z).(u);uu[alg]=z;residual(uu,p)[alg] end,u[alg])
            u[alg]-=J\r
        end
        @assert maximum(abs,residual(u,p)[alg])<1e-8
        u
    end
    ip=[SII.parameter_index(nw,VIndex(7,s)) for s in (:ZIPLoad₊Pset,:ZIPLoad₊Qset)]
    edge=SII.parameter_index(nw,EIndex(38,:piline₊active))
    checks=[]
    for (mode,active) in [("normal",1.0),("line",0.0)]
        p=copy(p0);p[edge]=active;u=consistent(u0[dyn],p)
        par(a)=begin local pp=eltype(a).(p);pp[ip].=p[ip].*(1+a[1]);pp end
        J=FD.jacobian(uu->residual(uu,p),u)
        Ju=FD.jacobian(a->residual(u,par(a)),[0.0])
        Vj=FD.jacobian(uu->volt(uu,p),u)
        Vp=FD.jacobian(a->volt(u,par(a)),[0.0])
        Zx=-(J[alg,alg]\J[alg,dyn]);Zu=-(J[alg,alg]\Ju[alg,:])
        A=Md\(J[dyn,dyn]+J[dyn,alg]*Zx)
        B=Md\(Ju[dyn,:]+J[dyn,alg]*Zu)
        C=Vj[:,dyn]+Vj[:,alg]*Zx;D=Vp+Vj[:,alg]*Zu
        force=Md\residual(u,p)[dyn]
        dir=joinpath(dest,mode);mkpath(dir)
        for (name,x) in [("J",J),("Ju",Ju),("H",Vj),("Hu",Vp),("Zx",Zx),("Zu",Zu),("A",A),("B",B),("C",C),("D",D),("force",force),("voltage",volt(u,p)),("state",u)]
            writearray(dir,name,x)
        end
        delta=sin.((1:length(u))*.731);delta/=norm(delta);h=1e-6
        fd=(residual(u+h*delta,p)-residual(u-h*delta,p))/(2h)
        native_error=norm(fd-J*delta)/max(norm(J*delta),1e-12)
        dx=sin.((1:length(dyn))*.619);dx/=norm(dx);h=1e-6
        up=consistent(u0[dyn]+h*dx,p);um=consistent(u0[dyn]-h*dx,p)
        fdf=Md\((residual(up,p)[dyn]-residual(um,p)[dyn])/(2h))
        fdv=(volt(up,p)-volt(um,p))/(2h)
        pp=par([h]);pm=par([-h]);up=consistent(u0[dyn],pp);um=consistent(u0[dyn],pm)
        fdb=Md\((residual(up,pp)[dyn]-residual(um,pm)[dyn])/(2h))
        fdd=(volt(up,pp)-volt(um,pm))/(2h)
        err(a,b)=norm(a-b)/max(norm(b),1e-12)
        row=Dict("mode"=>mode,"native_direction_error"=>native_error,"A_direction_error"=>err(fdf,A*dx),"C_direction_error"=>err(fdv,C*dx),"B_direction_error"=>err(fdb,vec(B)),"D_direction_error"=>err(fdd,vec(D)),"algebraic_residual"=>maximum(abs,residual(u,p)[alg]),"fixed_dynamic_state_error"=>maximum(abs,u[dyn]-u0[dyn]),"Gz_condition"=>cond(J[alg,alg]))
        if mode=="normal"
            row["descriptor_jacobian_relative_error"]=norm(J-Matrix(desc.A))/norm(J)
        end
        push!(checks,row)
        jsonwrite(joinpath(DEST,"DERIVATIVE_CHECKS.json"),checks)
        @assert maximum([row[k] for k in ["native_direction_error","A_direction_error","B_direction_error","C_direction_error","D_direction_error"]])<1e-5
        println("EXTRACTED ",JSON.json(row));flush(stdout)
    end
    jsonwrite(joinpath(DEST,"DIMENSIONS.json"),Dict("native"=>length(u0),"differential"=>length(dyn),"algebraic"=>length(alg),"differential_mass_min"=>minimum(mass[dyn]),"differential_mass_max"=>maximum(mass[dyn]),"input"=>"Fractional common P/Q setpoint change at bus 7","mode"=>"nominal or line 23-24 open; same differential reference"))
end
