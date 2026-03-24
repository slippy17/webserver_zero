import tinytuya

d = tinytuya.OutletDevice(
    dev_id= "002009362c3ae81ac71d",
    address= "192.168.0.208",
    local_key= "u?Z_c;?E8pns1'vK",
    version=3.3
    )
data = d.status() 
print('Device status: %r' % data)
