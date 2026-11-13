"""Deterministic PMU operator. No RAW data, event labels or future reports.

Input currents are Julia edge observables INTO their named terminal bus.
The frozen CT map is applied after converting to outward branch convention.
One common affine reference rotates V and I identically. Frequency and ROCOF
come from the reported voltage phase; an additional 60-Hz or bias term is not
applied elsewhere. This module does not claim rotor speed identification.
"""
import numpy as np

def wrap_deg(x):
    return (np.asarray(x)+180)%360-180

def unwrap_finite_deg(x):
    x=np.asarray(x,float); out=np.full_like(x,np.nan)
    for j in range(x.shape[1]):
        ids=np.flatnonzero(np.isfinite(x[:,j]))
        for group in np.split(ids,np.flatnonzero(np.diff(ids)>1)+1):
            if len(group):
                out[group,j]=np.rad2deg(np.unwrap(np.deg2rad(x[group,j])))
    return out

def phase_estimator(time, angle_deg, magnitude, window=21):
    """R5C.2 estimator structure: causal robust magnitude-weighted quadratic.

    Warm-up is explicit (four NaNs); missing samples break a segment rather
    than being bridged. Fits use only the current and preceding reports.
    """
    theta=unwrap_finite_deg(angle_deg)
    f=np.full_like(theta,np.nan); rocof=f.copy()
    for k in range(4,len(time)):
        start=max(0,k-window+1)
        for j in range(theta.shape[1]):
            yy=theta[start:k+1,j]; mag=magnitude[start:k+1,j]
            invalid=np.flatnonzero(~np.isfinite(yy)|~np.isfinite(mag)|(mag<=0))
            offset=int(invalid[-1]+1) if len(invalid) else 0
            yy=yy[offset:]; mag=mag[offset:]
            if len(yy)<5:
                continue
            tt=np.asarray(time)[start+offset:k+1]-time[k]
            design=np.column_stack((np.ones(len(tt)),tt,tt**2))
            weights=np.clip(mag/max(float(np.median(mag)),1e-12),.05,2)**2
            coef=np.linalg.lstsq(design*np.sqrt(weights)[:,None],yy*np.sqrt(weights),rcond=None)[0]
            for _ in range(2):
                residual=yy-design@coef
                scale=1.4826*np.median(abs(residual-np.median(residual)))+1e-9
                w=weights*np.minimum(1,1.5*scale/np.maximum(abs(residual),1e-12))
                coef=np.linalg.lstsq(design*np.sqrt(w)[:,None],yy*np.sqrt(w),rcond=None)[0]
            f[k,j]=60+coef[1]/360
            rocof[k,j]=2*coef[2]/360
    return f,rocof

def report(time, voltage_all_pu, native_terminal_current_pu, mapping, bus_kv, cfg):
    pmus=cfg['pmus']; t=np.asarray(time,float)
    reference=cfg['common_phase_intercept_deg']+cfg['common_phase_slope_deg_s']*t
    shifts=reference[:,None]+np.asarray(cfg['relative_voltage_bias_deg'])[None,:]
    v=voltage_all_pu[:,np.array(pmus)-1]*np.exp(1j*np.deg2rad(shifts))
    current=np.empty_like(v)
    for j,r in enumerate(mapping.itertuples()):
        assert int(r.pmu_bus)==pmus[j]
        base=100e6/(np.sqrt(3)*float(bus_kv[int(r.terminal)-1])*1000)
        outward=-native_terminal_current_pu[:,j]
        current[:,j]=outward*int(r.polarity)*base*float(r.gain)*np.exp(
            1j*np.deg2rad(shifts[:,j]+float(r.bias_deg)))
    f,rocof=phase_estimator(t,np.angle(v,deg=True),abs(v),window=21)
    return dict(voltage_pu=v,current_A=current,frequency_hz=f,rocof_hz_s=rocof)
