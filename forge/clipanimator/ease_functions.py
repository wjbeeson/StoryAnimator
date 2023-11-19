import functools
def constrain_ease(func):
    @functools.wraps(func)
    def wrapper_decorator(x):
        x = min(x,1.0)
        value = func(x)
        # Do something after
        return min(value,1.0)
    return wrapper_decorator
@constrain_ease
def easeLinear(x):
    return x

#@constrain_ease
def easeOutBack(x):
    c1 = 1.70158;
    c3 = c1 + 1;

    return 1 + c3 * pow(x - 1, 3) + c1 * pow(x - 1, 2);

@constrain_ease
def easeOutCubic(x):
    return 1 - pow(1 - x, 3);


