include(joinpath(@__DIR__,"initialize_frozen.jl"))
const DEST=joinpath(@__DIR__,"run")
mkpath(DEST)
cfg=JSON.parsefile(joinpath(@__DIR__,"protocol.json"))
nw,s0=initialize_frozen()
include(joinpath(@__DIR__,"extract_operators.jl"))
extract_operators(nw,s0)
gens=collect(30:39)
pars=CSV.read(joinpath(REF,"initial_parameters.csv"),DataFrame)
msym(g,s)=Symbol(g==39 ? "machine₊" : "ctrld_gen₊machine₊",s)
function param(g,s)
    i=findfirst(==(string(VIndex(g,g==39 ? s : Symbol("ctrld_gen₊",s)))),pars.symbol)
    @assert !isnothing(i)
    pars.value[i]
end
H=[param(g,:machine₊H) for g in gens]
Sn=[param(g,:machine₊Sn) for g in gens]
D=[param(g,:machine₊D) for g in gens]
Rs=[param(g,:machine₊R_s) for g in gens]
getmachines=SII.getsym(nw,[VIndex(g,msym(g,s)) for g in gens for s in ("ω","τ_m","τ_e","P","I_d","I_q")])
getV=SII.getsym(nw,[VIndex(g,Symbol("busbar₊u_",s)) for g in 1:39 for s in ("r","i")])
getI=SII.getsym(nw,[EIndex(e,Symbol(side,"₊i_",s)) for e in 1:46 for side in ("src","dst") for s in ("r","i")])
oi=[SII.variable_index(nw,VIndex(g,msym(g,"ω"))) for g in gens]
statuses=[]
for case in cfg["cases"]
    id=case["id"];u0=copy(uflat(s0));p0=copy(pflat(s0));ph=Dict(0.0 => copy(p0));left=Dict{Float64,Vector{Float64}}()
    ix=case["kind"]=="line" ? [SII.parameter_index(nw,EIndex(case["edge"],:piline₊active))] :
       [SII.parameter_index(nw,VIndex(case["bus"],s)) for s in (:ZIPLoad₊Pset,:ZIPLoad₊Qset)]
    function update!(integ)
        t=Float64(integ.t);left[t]=copy(integ.u)
        factor=abs(t-case["on"])<1e-9 ? (case["kind"]=="line" ? 0. : case["factor"]) : 1.
        integ.p[ix].=p0[ix].*factor
        ph[t]=copy(integ.p);save_parameters!(integ);SB.auto_dt_reset!(integ);SB.u_modified!(integ,true)
    end
    cb=IEEE39.DiffEqCallbacks.PresetTimeCallback([case["on"],case["off"]],update!;save_positions=(true,true))
    prob=ODEProblem(nw,u0,(0.,Float64(cfg["duration_s"])),copy(p0);add_nw_cb=cb)
    mass=diag(Matrix(prob.f.mass_matrix));dyn=findall(!iszero,mass);alg=findall(iszero,mass)
    times=collect(0:1/cfg["sample_hz"]:cfg["duration_s"])
    println("SOLVE ",id);flush(stdout)
    elapsed=@elapsed sol=solve(prob,Rodas5P();abstol=cfg["abstol"],reltol=cfg["reltol"],dtmax=cfg["dtmax_s"],saveat=times,save_everystep=false,maxiters=10^7)
    @assert string(sol.retcode)=="Success"
    ticks=Dict{Int,Int}()
    for (k,t) in enumerate(sol.t)
        n=round(Int,t*cfg["sample_hz"])
        abs(t-n/cfg["sample_hz"])<1e-8 && (ticks[n]=k)
    end
    data=zeros(length(times),60);vv=zeros(length(times),78);ii=zeros(length(times),184);dw=zeros(length(times),10)
    rhs=zeros(length(u0));algmax=0.;jump=0.
    for (k,t) in enumerate(times)
        u=sol.u[ticks[k-1]];p=ph[maximum(x for x in keys(ph) if x<=t+1e-9)]
        state=NWState(nw,u,p,t);data[k,:]=getmachines(state);vv[k,:]=getV(state);ii[k,:]=getI(state)
        nw(rhs,u,p,t);dw[k,:]=rhs[oi]./mass[oi];algmax=max(algmax,maximum(abs,rhs[alg]))
        if haskey(left,t);jump=max(jump,maximum(abs.(u[dyn]-left[t][dyn])));end
    end
    CSV.write(joinpath(DEST,id*"_machine.csv"),hcat(DataFrame(time_s=times),DataFrame(data,[Symbol("G",g,"_",s) for g in gens for s in ("omega","tm","te","P","Id","Iq")]),DataFrame(dw,[Symbol("G",g,"_domega") for g in gens])))
    CSV.write(joinpath(DEST,id*"_network.csv"),hcat(DataFrame(time_s=times),DataFrame(vv,[Symbol("V",g,"_",s) for g in 1:39 for s in ("r","i")]),DataFrame(ii,[Symbol("E",e,"_",side,"_",s) for e in 1:46 for side in ("src","dst") for s in ("r","i")])))
    status=Dict("case"=>id,"retcode"=>string(sol.retcode),"samples"=>length(times),"algebraic_residual"=>algmax,"dynamic_jump"=>jump,"seconds"=>elapsed)
    push!(statuses,status);jsonwrite(joinpath(DEST,"PHYSICS_STATUS.json"),statuses)
    println(JSON.json(status));flush(stdout)
end
jsonwrite(joinpath(DEST,"MACHINE_PARAMETERS.json"),Dict("buses"=>gens,"H"=>H,"Sn"=>Sn,"D"=>D,"Rs"=>Rs))
println("PHYSICS_COMPLETE")
