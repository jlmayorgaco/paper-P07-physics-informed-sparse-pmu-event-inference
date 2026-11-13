using IEEE39, PowerDynamics, NetworkDynamics
using OrdinaryDiffEqRosenbrock, OrdinaryDiffEqNonlinearSolve
using CSV, DataFrames, JSON, LinearAlgebra, SHA
using NetworkDynamics: SII
const SB = NetworkDynamics.SciMLBase
const ROOT = @__DIR__
const REF = normpath(joinpath(ROOT,"..","hamiltonian_f01_20261113","reproduction","reference"))
jsonwrite(path,x)=open(io->JSON.print(io,x,2),path,"w")

function initialize_frozen()
    for f in readdir(joinpath(REF,"ieee39_source"))
        @assert sha256(read(joinpath(pkgdir(IEEE39),"src",f))) == sha256(read(joinpath(REF,"ieee39_source",f)))
    end
    println("BUILD_FROZEN_PLANT");flush(stdout)
    nw=IEEE39.set_IEEE39_PF_init(IEEE39.get_IEEE39_base())
    archived=CSV.read(joinpath(REF,"pd_static_solution.csv"),DataFrame)
    for b in (31,39)
        row=archived[archived.bus.==b,:][1,:]
        set_default!(nw[VIndex(b)],:ZIPLoad₊Vset,hypot(row.u_r,row.u_i))
    end
    pfnw=powerflow_model(nw);pfs0=NWState(pfnw)
    targets=CSV.read(joinpath(REF,"target_bus_state.csv"),DataFrame)
    buses=CSV.read(joinpath(REF,"data","bus.csv"),DataFrame)
    for row in eachrow(buses)
        b=Int(row.bus);r=targets[targets.bus.==b,:][1,:]
        if row.bus_type=="PQ"
            pfs0.v[b].p[:pq₊P]=r.p_injection_pu;pfs0.v[b].p[:pq₊Q]=r.q_injection_pu
        elseif row.bus_type=="PV"
            pfs0.v[b].p[:pv₊P]=r.p_injection_pu;pfs0.v[b].p[:pv₊V]=r.vm_pu
        else
            pfs0.v[b].p[:slack₊V]=r.vm_pu
        end
    end
    pfs=solve_powerflow(nw;pfnw,pfs0,verbose=false)
    s0=initialize_from_pf!(nw;pfs,verbose=false)
    old_u=CSV.read(joinpath(REF,"initial_state.csv"),DataFrame)
    old_p=CSV.read(joinpath(REF,"initial_parameters.csv"),DataFrame)
    @assert string.(SII.variable_symbols(nw))==old_u.symbol
    @assert string.(SII.parameter_symbols(nw))==old_p.symbol
    udiff=maximum(abs.(uflat(s0).-old_u.value));pdiff=maximum(abs.(pflat(s0).-old_p.value))
    @assert udiff<1e-10 && pdiff<1e-10
    # Use the archived vectors exactly after checking fresh recovery.
    uflat(s0).=old_u.value;pflat(s0).=old_p.value
    du=zeros(length(uflat(s0)));nw(du,uflat(s0),pflat(s0),0.)
    jsonwrite(joinpath(ROOT,"diagnostics","frozen_initialization.json"),Dict(
        "recovered_state_max_difference"=>udiff,"recovered_parameters_max_difference"=>pdiff,
        "used_exact_archived_vectors"=>true,"initial_residual"=>maximum(abs,du),
        "julia"=>string(VERSION),"PowerDynamics"=>string(Base.pkgversion(PowerDynamics)),
        "NetworkDynamics"=>string(Base.pkgversion(NetworkDynamics)),"IEEE39"=>string(Base.pkgversion(IEEE39))))
    println("INITIAL_STATE_VERIFIED");flush(stdout)
    return nw,s0
end

