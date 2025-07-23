from pipython import GCSDevice

ip = '169.254.5.112'
port = 50000

with GCSDevice('C-887') as pidevice:
    pidevice.ConnectTCPIP(ip, port)
    print('Connected:', pidevice.qIDN())

    # Get available axes
    axes = pidevice.qSAI()
    print('Axes:', axes)

    # Enable servo on all axes
    pidevice.SVO(axes, [True]*len(axes))

    # Home all axes (if needed)
    # pidevice.FNL(axes)
    # pidevice.WaitOnTarget()

    # Move hexapod to (X, Y, Z, U, V, W)
    target_pos = {'X': 1.0, 'Y': 0.5, 'Z': 0.0, 'U': 0.0, 'V': 0.0, 'W': 0.0}
    pidevice.MOV(target_pos)
    pidevice.WaitOnTarget()

    # Query position
    current_pos = pidevice.qPOS()
    print('Current Position:', current_pos)

    # Turn off servo (optional)
    pidevice.SVO(axes, [False]*len(axes))
