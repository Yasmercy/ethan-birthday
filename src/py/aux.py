def fit_bounds(x, lower, higher):
    return max(min(x, higher), lower)

def in_bounds(cx, cy, x0, y0, x1, y1):
    return x0 <= cx <= x1 and y0 <= cy <= y1

def corners(cx, cy, w, h):
    return [
        (cx - w, cy - h),
        (cx + w, cy - h),
        (cx + w, cy + h),
        (cx - w, cy + h)
    ]
