def numsuffix(num):
    if int(num)%10==1: return f'{num}st'
    elif int(num)%10==2: return f'{num}nd'
    elif int(num)%10==3: return f'{num}rd'
    else: return f'{num}th'

def statmod(stat):
    return int((stat-10)//2)

def rgb2hex(rgb):
    r, g, b = rgb[0],rgb[1],rgb[2]
    return f'#{r:02x}{g:02x}{b:02x}'