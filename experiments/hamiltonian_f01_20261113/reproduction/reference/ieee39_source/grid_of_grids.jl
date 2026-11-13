
using Graphs
using Random
using PowerDynamics
using CSV
using DataFrames

"""
    build_IEEE39_grid_of_grids(N; pert=0.1, p_omit=0.2, n_inter_lines=2,
                               rng=Random.default_rng(), max_tries=60,
                               u_min=0.9, u_max=1.1,
                               distributed_slack=false)

Build an `N×N` lattice of IEEE39 grid copies wired together into a single large
`Network` and return `(nw_large, nws_init)`. One-off helper for large-network
experiments.

  - Copies are placed on an `N×N` lattice (copy index `r*N + c`, with `r,c` in
    `0:N-1`). Each pair of right/down neighbours is joined by `n_inter_lines`
    extra lines (default 2), each with parameters copied from a random existing
    transmission line (transformer branches with off-nominal turns ratio are
    excluded: as ties they impose fixed voltage steps that push regions out of
    the voltage band), connecting two random buses (one in each neighbouring
    copy; the lines of one pair use distinct bus pairs).
  - Only the copy in the centre of the lattice keeps its slack/lead bus (bus 31);
    in every other copy bus 31 is turned into a PV bus (`distributed_slack=false`,
    default) or a distributed-slack follower (`distributed_slack=true`), so the
    whole grid has a single reference point.
  - With `distributed_slack=true` the slack duty is shared across all bus-31
    instances via a global balance variable `γ`: the lead (centre copy) fixes
    voltage magnitude and angle and broadcasts `γ`; each follower adjusts its net
    injection as `P = Pbase + (1-γ)·|Pbase|`.
  - Each machine-only generator bus in 30, 32–37 in each copy is independently
    dropped with probability `p_omit` and becomes a junction (Kirchhoff) bus.
    Buses 31 (slack/lead), 38 and 39 are never dropped: 39 models the
    aggregated external system, whose ~11 p.u. load cannot be supplied without
    the co-located machine and whose lines' large shunt charging overvolts the
    corridor without the load; 38 is the only voltage support of the
    high-charging 26–28–29 corner. To keep each copy roughly self-balanced, the
    copy's PQ loads are scaled down by the dropped generation.
  - The power flow is then varied systematically, following the
    `ieee39_random_pf.jl` semantics: every generator power and every load power is
    scaled by `(1 + pert·randn())`. At the generator+load buses (39, and 31
    wherever it exposes a `"P"` setpoint — PV in standard mode, or lead/follower in
    distributed-slack mode) the generator and load powers are varied independently.
    Only the standard-mode central slack has no `"P"` setpoint; there just its load
    is varied (the slack absorbs the global imbalance).

A converged power flow is only accepted if every bus voltage magnitude lies
within `[u_min, u_max]` (default `[0.9, 1.1]` p.u.) and every machine
initializes with non-negative mechanical torque (`τ_m ≥ 0`, its model bound) —
the random draws regularly produce converged but operationally invalid
operating points, and the slack machine can be pushed into consuming.

Because the random draws occasionally produce a power flow that does not
converge (or violates the voltage band), the whole construction is retried with
fresh draws (advancing `rng`) in rounds of 3 attempts: after each failed round
every active and reactive power injection — generation and load alike — is
reduced by a further 5%, lowering the network loading until a stable,
voltage-compatible power flow is found. `max_tries` (default 60, i.e. up to 19
reduction steps ≈ 62% total reduction) caps the total number of attempts.
"""
build_IEEE39_grid_of_grids(N; kwargs...) =
    with_ieee39_bases(() -> _build_IEEE39_grid_of_grids(N; kwargs...))

function _build_IEEE39_grid_of_grids(N; pert=0.1, p_omit=0.2, n_inter_lines=2,
                                     rng=Random.default_rng(), max_tries=60,
                                     u_min=0.9, u_max=1.1,
                                     distributed_slack=false)
    nw_39 = set_IEEE39_PF_init(get_IEEE39_base())
    n_vert = nv(nw_39)
    1 <= n_inter_lines <= n_vert^2 || throw(ArgumentError(
        "n_inter_lines must be in 1:$(n_vert^2) (distinct bus pairs between two copies), got $n_inter_lines"))
    n_copies = N * N
    center_sni = (N ÷ 2) * N + (N ÷ 2)   # the single copy that keeps its slack

    vms = nw_39[VIndex(:)]
    ems = nw_39[EIndex(:)]

    # Inter-copy tie templates: true transmission lines only. 11 of the 46
    # IEEE39 branches are transformers with off-nominal turns ratio (down to
    # 0.9346); copied as a tie between two random buses they impose a fixed
    # ~7% voltage step that no injection scaling can compensate — chained taps
    # drove whole regions out of the voltage band at larger N (u_mag ≈ 1.21 at
    # N=5) and made every retry fail.
    tie_templates = [em for em in ems
                     if get_default(em, :piline₊r_src) == 1.0 == get_default(em, :piline₊r_dst)]

    # Reuse an existing, tested bus model as template when a machine is dropped.
    junction_template = nw_39[VIndex(1)]   # pure Kirchhoff bus
    # Droppable machine buses. 31 is kept as the (distributed) slack. Two more
    # machines are never dropped because a region's voltage depends on them and
    # the band violation probability goes → 1 with N otherwise:
    #  - 39, the aggregated external-system equivalent: its ~11 p.u. load
    #    cannot be supplied without the co-located machine (the weak 1–39/9–39
    #    corridor collapses to u ≈ 0.4–0.9), and without the load the same
    #    lines' huge shunt charging (B ≈ 0.75/1.2 p.u.) drives u ≈ 1.10–1.12.
    #  - 38, the only machine at the high-charging 26–28–29 corner: with it
    #    dropped in a load-shed copy, buses 28/29 float to u ≈ 1.10–1.13.
    gen_buses = [30, 32, 33, 34, 35, 36, 37]
    machine_buses = vcat(gen_buses, [31, 38, 39])  # buses carrying a machine model

    # Load setpoints of the two generator+load buses.
    load_P31 = get_default(nw_39[VIndex(31)], :ZIPLoad₊Pset)
    load_Q31 = get_default(nw_39[VIndex(31)], :ZIPLoad₊Qset)
    load_P39 = get_default(nw_39[VIndex(39)], :ZIPLoad₊Pset)
    load_Q39 = get_default(nw_39[VIndex(39)], :ZIPLoad₊Qset)

    # Nominal power-flow setpoints, read straight from the base pf model.
    base_pf = NWState(powerflow_model(nw_39))
    genP = Dict(b => base_pf.v[b].p["P"] for b in gen_buses)        # scheduled gen (bus 39: net)
    pq_load_buses = [b for b in 1:n_vert if (:ZIPLoad₊Pset in nw_39[VIndex(b)].psym) && b ∉ (31, 39)]
    L_pq = sum(abs(base_pf.v[b].p["P"]) for b in pq_load_buses)     # total PQ load magnitude

    # PV setpoint for the bus-31 slacks we convert to PV: the slack's reference
    # net injection and voltage from the bus table.
    bus_df = CSV.read(joinpath(DATA_DIR, "bus.csv"), DataFrame)
    row31 = bus_df[findfirst(==(31), bus_df.bus), :]
    P31_pv, V31 = row31.P, row31.V

    subname(sni, name) = Symbol("net$(sni)_$(name)")
    gv(sni, b) = n_vert * sni + b

    function attempt(power_scale)
        nw_vertices = []
        nw_edges = []
        load_factor = ones(n_copies)
        omit_per_copy = [Int[] for _ in 1:n_copies]
        for sni in 0:(n_copies - 1)
            offset = n_vert * sni

            # Decide omissions for this copy and how much load to shed to compensate.
            omit = [b for b in gen_buses if rand(rng) < p_omit]
            omit_per_copy[sni + 1] = omit
            # Generation removed: the dropped PV buses' scheduled power.
            P_lost = sum(genP[b] for b in omit; init=0.0)
            f = clamp((L_pq - P_lost) / L_pq, 0.05, 1.0)
            load_factor[sni + 1] = f

            for vm in vms
                b = get_graphelement(vm)
                gvidx = offset + b
                if b in omit
                    # Dropped machine bus -> junction (Kirchhoff) bus.
                    rep = VertexModel(copy(junction_template); vidx=gvidx, name=subname(sni, "bus$b"))
                    push!(nw_vertices, rep)
                else
                    vmc = VertexModel(copy(vm); vidx=gvidx, name=subname(sni, vm.name))
                    if b == 31
                        lead_vidx = gv(center_sni, 31)
                        if distributed_slack
                            if sni == center_sni
                                set_pfmodel_with_bases!(vmc, dist_slack_lead_current_source(
                                    P=P31_pv, V=V31, δ=0, idx=gvidx))
                            else
                                set_pfmodel_with_bases!(vmc, dist_slack_follow_current_source(
                                    P=P31_pv, V=V31, idx=gvidx, lead_vidx=lead_vidx))
                            end
                        elseif sni != center_sni
                            set_pfmodel_with_bases!(vmc, pfPV(P=P31_pv, V=V31))
                        end
                    end
                    push!(nw_vertices, vmc)
                end
            end
            for em in ems
                ge = get_graphelement(em)
                push!(nw_edges, EdgeModel(copy(em); src=ge.src + offset, dst=ge.dst + offset))
            end
        end

        # Wire neighbouring copies on the lattice (right + down neighbours):
        # `n_inter_lines` random lines per neighbouring pair, on distinct bus
        # pairs so no duplicate parallel edge is created.
        for r in 0:(N - 1), c in 0:(N - 1)
            sni = r * N + c
            for nb in (c < N - 1 ? sni + 1 : nothing, r < N - 1 ? sni + N : nothing)
                isnothing(nb) && continue
                pairs = Tuple{Int,Int}[]
                while length(pairs) < n_inter_lines
                    src = rand(rng, 1:n_vert) + n_vert * sni
                    dst = rand(rng, 1:n_vert) + n_vert * nb
                    (src, dst) in pairs && continue
                    push!(pairs, (src, dst))
                    em = rand(rng, tie_templates)
                    push!(nw_edges, EdgeModel(copy(em); src, dst))
                end
            end
        end

        nw_large = Network(nw_vertices, nw_edges; warn_order=false)

        # --- systematic power-flow variation, cf. generate_powerflow_variation ---
        pfnw = powerflow_model(nw_large)
        pfs = NWState(pfnw)
        internal_variations = Dict()

        # 1. At the generator+load buses remove the load from the net injection so
        #    that the global scaling below varies the generator power alone. Per the
        #    `ieee39_random_pf.jl` semantics, bus 31 exposes its `Pbase` as `"P"` in
        #    distributed-slack mode too (lead at the centre, follower elsewhere), so
        #    its load is subtracted and re-added just like a pfPV bus. The only bus
        #    without a `"P"` setpoint is the standard-mode central slack.
        for sni in 0:(n_copies - 1)
            39 ∉ omit_per_copy[sni + 1] && (pfs.v[gv(sni, 39)].p["P"] -= load_P39)
            (distributed_slack || sni != center_sni) && (pfs.v[gv(sni, 31)].p["P"] -= load_P31)
        end
        # 2. Shed each copy's PQ loads to compensate the generation it dropped.
        for sni in 0:(n_copies - 1)
            f = load_factor[sni + 1]
            f == 1 && continue
            for b in pq_load_buses
                pfs.v[gv(sni, b)].p["P"] *= f
                pfs.v[gv(sni, b)].p["Q"] *= f
            end
        end
        # 3. Vary every generator and load power.
        pfs.v[:].p["P"] .*= (1 .+ pert .* randn(rng, length(pfs.v[:].p["P"])))
        pfs.v[:].p["Q"] .*= (1 .+ pert .* randn(rng, length(pfs.v[:].p["Q"])))
        # 4. Vary the loads of the generator+load buses independently and add them
        #    back to the net injection (see the per-bus note below for which buses
        #    expose a "P" setpoint vs. only an initialization override).
        for sni in 0:(n_copies - 1)
            if 39 ∉ omit_per_copy[sni + 1]
                P_39 = (1 + pert * randn(rng)) * load_P39
                Q_39 = (1 + pert * randn(rng)) * load_Q39
                pfs.v[gv(sni, 39)].p["P"] += P_39
                internal_variations[VIndex(gv(sni, 39), :ZIPLoad₊Pset)] = P_39
                internal_variations[VIndex(gv(sni, 39), :ZIPLoad₊Qset)] = Q_39
            end
            P_31 = (1 + pert * randn(rng)) * load_P31
            Q_31 = (1 + pert * randn(rng)) * load_Q31
            # Add the independently-varied load back to bus 31's net injection
            # wherever it exposes a "P" setpoint: every copy in DS mode (lead +
            # followers) and every non-central copy in standard mode (pfPV). The
            # standard-mode central slack has no "P" and is varied via the override.
            (distributed_slack || sni != center_sni) && (pfs.v[gv(sni, 31)].p["P"] += P_31)
            internal_variations[VIndex(gv(sni, 31), :ZIPLoad₊Pset)] = P_31
            internal_variations[VIndex(gv(sni, 31), :ZIPLoad₊Qset)] = Q_31
        end

        # 5. Global power reduction (see the retry loop): scale every injection —
        #    generation and load alike — so the network keeps its balance while
        #    the overall loading drops. The independently-varied gen+load bus
        #    load setpoints must be scaled too, or the dynamic model would be
        #    initialized with loads inconsistent with the power flow.
        if power_scale != 1.0
            pfs.v[:].p["P"] .*= power_scale
            pfs.v[:].p["Q"] .*= power_scale
            for (k, v) in internal_variations
                internal_variations[k] = v * power_scale
            end
        end

        # Equivalent to `solve_powerflow(nw_large; pfnw, pfs0=pfs)` but with a
        # capped iteration budget: converging GoG power flows need well under
        # 100 iterations, while a diverging draw otherwise grinds through the
        # solver's full default budget (~30 min at N=5) before the retry loop
        # can move on to a fresh draw.
        pfs = find_fixpoint(pfnw, pfs; maxiters=250)

        # Reject converged but operationally invalid solutions: every bus
        # voltage magnitude must lie within the steady-state band.
        umag = pfs[VIndex(1:nv(nw_large), :busbar₊u_mag)]
        viol = findall(u -> !(u_min <= u <= u_max), umag)
        if !isempty(viol)
            worst = sort(viol; by=i -> -abs(umag[i] - 1.0))[1:min(end, 3)]
            detail = join(("bus $i (copy $(div(i - 1, n_vert)), local bus " *
                           "$(mod1(i, n_vert))): u=$(round(umag[i], digits=4))" for i in worst), ", ")
            error("power flow voltage out of bounds ($(length(viol)) buses outside " *
                  "[$u_min, $u_max]): $detail")
        end

        # Machine rotor-angle guesses: the stock guesses (δ ≈ 0, dq-frame
        # quantities near their base values) are tuned to the single-copy
        # network, where bus angles stay near zero. On the lattice, buses far
        # from the (distributed) slack sit at large absolute angles, and the
        # component-wise machine init then cycles without converging from the
        # δ=0 basin (MaxIters, observed in corner copies). The dq-local guesses
        # remain valid in any frame — only δ must follow the terminal angle.
        guess_overrides = Dict{VIndex,Float64}()
        for sni in 0:(n_copies - 1), b in machine_buses
            b in omit_per_copy[sni + 1] && continue
            gi = gv(sni, b)
            δsym = b == 39 ? (:machine₊δ) : (:ctrld_gen₊machine₊δ)
            guess_overrides[VIndex(gi, δsym)] = pfs[VIndex(gi, :busbar₊u_arg)]
        end

        nws = initialize_from_pf(nw_large; pfs, tol=1e-3, nwtol=1e-3,
            guess_overrides,
            default_overrides=merge(interface_values(pfs), internal_variations), verbose=false)

        # Floor the machine torque at zero: reject operating points where any
        # machine initializes with negative mechanical torque (a generator
        # pushed into consuming). Even with all scheduled generation positive
        # the slack absorbs the global imbalance, so its machine can end up
        # negative — especially after the power reductions above. Such draws
        # are retried like a voltage-band violation instead of leaving a
        # nonphysical steady state (τ_m is bounded to [0, ∞) in the model).
        for sni in 0:(n_copies - 1), b in machine_buses
            b in omit_per_copy[sni + 1] && continue
            τsym = b == 39 ? (:machine₊τ_m) : (:ctrld_gen₊machine₊τ_m)
            τ = nws[VIndex(gv(sni, b), τsym)]
            τ < -1e-8 && error("machine torque negative at bus $(gv(sni, b)): τ_m = $τ")
        end

        return nw_large, nws
    end

    # Attempts run in rounds of 3: if no stable, voltage-compatible power flow is
    # found within a round, all active and reactive injections are reduced by a
    # further 5% for the next round, lowering the loading until a valid operating
    # point exists (capped at `max_tries` total attempts).
    power_scale = 1.0
    for attempt_i in 1:max_tries
        try
            return attempt(power_scale)
        catch err
            # Only a bad random draw (non-converging power flow / voltage-band
            # violation / failed initialization) is worth retrying with fresh
            # draws. Never mask a user interrupt or a genuine programming error
            # behind the retry loop — rethrow those immediately so they surface
            # instead of being retried `max_tries` times.
            err isa Union{InterruptException, MethodError,
                          UndefVarError, TypeError} && rethrow()
            attempt_i == max_tries && rethrow()
            attempt_i % 3 == 0 && (power_scale *= 0.95)
        end
    end
    error("build_IEEE39_grid_of_grids: no stable power flow within voltage bounds after $max_tries attempts")
end
