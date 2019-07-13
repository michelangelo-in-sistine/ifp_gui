# ifp_protocol.py
#

from ctypes import *
from hexutil import *
from powermesh import *

DEBUG_ON = False

class IfpProtocol():
    
    def __init__(self, biway_pipe_chain, ifpp_uid, pipe_id = 1):
        '''  ifpp_uid: 12-B str
             pipe_description: 16-B str'''
        valid_xmode = {'10', '20', '40', '80',
                       '11', '21', '41', '81',
                       '12', '22', '42', '82'}
        ifpp_uid = nospace(ifpp_uid)
        biway_pipe_chain = nospace(biway_pipe_chain)

        # init parameter check
        assert pipe_id <= 3, pipe_id
        assert len(ifpp_uid) == 12, ifpp_uid
        assert len(biway_pipe_chain) % 16 == 0, biway_pipe_chain
        for i in xrange(len(biway_pipe_chain) / 16):
            assert biway_pipe_chain[i*16+12:i*16+14] in valid_xmode, biway_pipe_chain[i*16+12:i*16+14] + ' in ' +biway_pipe_chain
            assert biway_pipe_chain[i*16+14:i*16+16] in valid_xmode, biway_pipe_chain[i*16+14:i*16+16] + ' in ' +biway_pipe_chain

        # class property storage
        self.biway_pipe_chain = biway_pipe_chain    #biway pipe description
        self.single_way_pipechain = biway_pipechain_to_singleway_pipechain(biway_pipe_chain,ifpp_uid)   #convert biway to singleway
        self.ifpp_uid = ifpp_uid
        self.target_uid = biway_pipe_chain[-16:-4]
        self.index = 0
        self.pipe_id = pipe_id
        self.passwd = 'FFFF'
        

        # frame object preparation
        self.frm = IfpFrame()                      #gen a static object, and fill domains that will not be changed during the transaction
        self.frm.type = hexstr2dec(self.biway_pipe_chain[12:14]) + 0x04
        for i in range(6):
            self.frm.dest[i] = hexstr2dec(self.biway_pipe_chain[i*2:(i+1)*2])
            self.frm.src[i] = hexstr2dec(self.ifpp_uid[i*2:(i+1)*2])


    def get_index(self):
        temp = self.index
        self.index = (self.index + 1) % 8           # index auto increment
        return temp
    
    def gen_setup_frame(self):
        ''' return a ifp pipe setup frame '''
        if(len(self.biway_pipe_chain)>16):
            consignee = False
        else:
            consignee = True

        self.frm.ctrl = 0x80 + consignee*0x40 + (self.pipe_id<<3) + self.get_index()
        self.index = 0

        body = self.single_way_pipechain[14:]

        self.frm.load_len = len(body)/2
        for i in xrange(self.frm.load_len):
            self.frm.load[i] = hexstr2dec(body[i*2:(i+1)*2])

        return self.frm.finish()

    def gen_appload_frame(self,app_body):
        '''Return a appload frame using the setuped pipe
            app_body: a str type variable (not hex str!) that will be transport as app load
        '''

        assert len(app_body)<sizeof(self.frm.load)
       
        self.frm.ctrl = (self.pipe_id<<3) + self.get_index()
        self.frm.load_len = len(app_body)
        for i in xrange(self.frm.load_len):
            self.frm.load[i] = ord(app_body[i])
        return self.frm.finish()

    def gen_sync_frame(self):
        frame = self.gen_appload_frame(hexstr2str(self.passwd+'AC'))
        self.index = 0
        return frame
    
    def gen_bgsync_frame(self):
        frame = self.gen_appload_frame(hexstr2str(self.passwd+'CA'))    #back door sync, not check password
        self.index = 0
        return frame

    def gen_reset_node_frame(self):
        return self.gen_appload_frame(hexstr2str(self.passwd+'12'))

    def gen_erase_usercode_frame(self):
        return self.gen_appload_frame(hexstr2str(self.passwd+'20'))

    def gen_erase_nvr_frame(self):
        return self.gen_appload_frame(hexstr2str(self.passwd+'21'))

    def gen_prgm_usercode_frame(self,start_addr,code):
        '''start_addr: int program start address
            code: str of code
        '''
        return self.gen_appload_frame(hexstr2str(self.passwd+'31'+('%04X'%start_addr)) + chr(len(code)) + code)

    def calc_timeout(self):
        ''' Calculate a ifp frame and its response transmission time according the pipe assigned

            After a ifp frame is generated (pipe setup, sync, app load, etc. ) by IfpFrame.finish()
            the packets length is fixed, so the transmission timing is fixed

            Returns:
                totol cost time(second)
        '''
        down_sum = 0
        up_sum = 0
        for i in xrange(len(self.biway_pipe_chain)/16):
            rate_set = {'0':1, '1':15, '2':63}
            down_sum += rate_set[self.biway_pipe_chain[i*16+13]]
            up_sum += rate_set[self.biway_pipe_chain[i*16+15]]

        if DEBUG_ON:
            print 'down_sum=%d,up_sum=%d,self.frm.frame_len=%d'%(down_sum,up_sum,self.frm.frame_len)
            print phy_trans_sticks(self.frm.frame_len, rate=0, scan=0, use_rscodec=False)
            print phy_trans_sticks(19, rate=0, scan=0, use_rscodec=False)
        plc_time_out = (phy_trans_sticks(self.frm.frame_len, rate=0, scan=0, use_rscodec=False) * down_sum +
                     phy_trans_sticks(19, rate=0, scan=0, use_rscodec=False) * up_sum)

        usart_time_out = (self.frm.frame_len + 4)/38400 + (19 + 4)/38400
        
        return plc_time_out/1000 + usart_time_out + 2


class IfpFrame(Structure):
    _pack_ = 1
    _fields_ = [('type',c_ubyte),
                ('len',c_ubyte),
                ('dest',c_ubyte*6),
                ('ctrl',c_ubyte),
                ('cs',c_ubyte),
                ('src',c_ubyte*6),
                ('load',c_ubyte*237)]
    def __init__(self):
        self.load_len = 0
        self.frame_len = 0

    def finish(self):
        '''calc len, cs, crc'''
        self.len = 18 + self.load_len
        
        frm = string_at(addressof(self),9)
        frm = str2dec(frm)
        self.cs = 256 - (sum(frm) % 256)

        frm = string_at(addressof(self),self.load_len+16)
        frm = str2dec(frm)
        [crc_h,crc_l] = calc_crc(frm)
        self.load[self.load_len] = crc_h
        self.load[self.load_len+1] = crc_l
        
        self.frame_len = self.load_len + 18
        return string_at(addressof(self),self.frame_len)


##class HostFrame(Structure):
##    _pack_ = 1
##    _fields_ = [('cmd',c_ubyte),
##                ('length',c_ubyte),
##                ('body',c_ubyte*sizeof(IfpFrame)),
##                ('crc',c_ubyte*2)]



def gen_host_command(cmd,body=''):
    ''' return a byte string '''
    ifp_cmd={'uid_query':0x51,
             'plc_package':0x53}

    command_length = len(body) + 4
    assert command_length<=255, 'too long host frame body length {0}'.format(len(body))
    command = chr(ifp_cmd[cmd])+chr(command_length)+body
    command = command + calc_crc(command)
    return command


def biway_pipechain_to_singleway_pipechain(biway_pipechain,ifpp_uid):
    '''convert powermesh biway pipe description to ifp single way description
        before conversion: uid1 xmode1 rmode1 uid2 xmode2 rmode2 ... targetuid xmode rmode
        after conversion:  xmode1 uid1 xmode2 uid2 ... xmode targetuid rmode uid(n-1) ... rmode2 uid1 rmode1 ifpp_uid
    '''
    biway_pipechain = nospace(biway_pipechain)
    ifpp_uid = nospace(ifpp_uid)
    stage = len(biway_pipechain)//16
    pipe = []
    for i in xrange(stage):
        if(i==stage-1):
            pipe.append(dec2hexstr(hexstr2dec(biway_pipechain[i*16+12 : i*16+14])+0x08))    #consignee mark
        else:
            pipe.append(biway_pipechain[i*16+12 : i*16+14])
        pipe.append(biway_pipechain[i*16 : i*16+12])

    for i in xrange(stage-2,-1,-1):
        pipe.append(biway_pipechain[(i+1)*16+14 : (i+1)*16+16])
        pipe.append(biway_pipechain[i*16 : i*16+12])

    pipe.append(biway_pipechain[14:16])
    pipe.append(ifpp_uid)
    
    return ''.join(pipe)


if __name__=='__main__':
    
    frame = gen_host_command('uid_query')
    print str2hexstr(frame)

    ifp_entity = IfpProtocol(ifpp_uid='5E 1D 0A 07 7F 87 ', biway_pipe_chain = '0B9A090A272D 2020 0B9A090A272D 2121')

    print str2hexstr(gen_host_command('plc_package',ifp_entity.gen_setup_frame()))
    print ifp_entity.calc_timeout()
    
    print str2hexstr(gen_host_command('plc_package',ifp_entity.gen_sync_frame()))
    print ifp_entity.calc_timeout()

    print str2hexstr(gen_host_command('plc_package',ifp_entity.gen_prgm_usercode_frame(0,'1234567890')))
    print ifp_entity.calc_timeout()
    
