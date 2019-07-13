#! /usr/bin/env python2.7
# -*- coding: cp936 -*-
#

import sys
import pickle
from hexutil import *
from hexfileutil import *
from myserial import *
from powermesh import *
from ifp_protocol import *

MAX_APP_LOAD = 103      #ifp_buffer为128字节,减dll开销18,security code 2,命令字1,长度1,地址2,最长负荷104字节,接收需要多一个字节E6, 因此最大103字节
DEBUG_ON = 0

class IfpFatalException(Exception):
    ''' The exceptions when raised the whole process should quit'''
    pass


class IfpException(Exception):
    ''' all exceptions when raised the current node update transaction should be broken
        but the next node update should start'''
    pass

def display_output(s, *other_s):
    ''' this function can be overload when the module is imported by higher-level framework, e.g. a GUI program
        so the output can be redirected to another interface.
    '''
    for t in other_s:
        s += t
    print s

def is_ifpp_response_valid(response):
    if(len(response)>0 and calc_crc(str2dec(response))==[226,240]):
        if(ord(response[0])==0x80):
            return True
        else:
            display_output("Error IFPP Response:", str2hexstr(response))
    return False


def check_ifpp(ser):
    '''check ifpp, if correct, return ifpp uid'''

    command = gen_host_command('uid_query')
    ifpp_uid = ''

    response = uart_switch(ser,command,0.5)
    if(is_ifpp_response_valid(response)):
        ifpp_uid = response[2:8]
    else:
        ##raise IfpFatalException("ifpp no response")
        display_output("ifpp no response")

    return str2hexstr(ifpp_uid)


def ifp_transaction(ser, host_command, timeout):
    ''' Basic ifp communication transaction control with another node via ifpp

        1. when host crc error, retry.
        2. when communication timeout, retry up to two times


        Args:
            ser: a opened usart com object
            host_command: pc command frame to ifpp(str type)
            timeout: max wait time(second)

        Returns:
            ifpp response retrieved from remote node(str type)

        Raises:
            IfpException: An error occurred when no response received after retry
    '''

    for i in xrange(3):
        display_output('>>', str2hexstr(host_command))
        time_start = time.clock()
        response = uart_switch(ser, host_command, timeout)
        if is_ifpp_response_valid(response):
            break;
    else:
        display_output(str2hexstr(response))
        raise IfpException("ifp timeout")

    display_output('<<', str2hexstr(response), '\n')
    #display_output('time estimate:%f, actually:%f, diff:%f'%(timeout,time.clock()-time_start,(timeout-(time.clock()-time_start))))
    return response


def ifp_app_transaction(ser, host_command, timeout):
    for i in xrange(3):
        response = ifp_transaction(ser, host_command, timeout)
        sta = ord(response[18])
        if(sta == 0x80):
            return response
        elif(sta == 0xF0):
            errorcode = ord(response[19])
            if(errorcode == 0x10):
                raise IfpFatalException("unsupport cmd")
            elif(errorcode == 0x20):
                raise IfpFatalException('integration error')
            elif(errorcode == 0x30):
                raise IfpException('security code error')
            elif(errorcode == 0x40):
                display_output('index error')
                self_next_index = (ord(host_command[10])+1) % 8
                new_index = ord(response[10]) % 8                   # index error 表示target已经成功接收到了上一包, 返回的index应该永远比己方大1
                if self_next_index != new_index:
                    raise IfpException('index control error, next:%X, return:%x' % (ifp_entity.index, new_index))
                else:
                    return
            elif(errorcode == 0x50):
                raise IfpException('flash burn error')
            else:
                raise IfpFatalException('unknown error code')
        else:
            raise IfpFatalException('unknown error code')

def response_others():
    pass


def ifp_burn(ser,ifpp_uid, pipe_script, data_buffer, data_chips):
    '''
        ifp burn a hex image to target node
        ifpp_uid: ifpp uid hex string
        pipe_script: pipe descript string. e.g. '5e1d0a051122 2020' or '5e1d0a051122 2020 5e1d0a053344 1020'
        data_buffer: hex image, a 32768 x 1 byte array
        data_chips:  
    '''
    ifp_entity = IfpProtocol(ifpp_uid=ifpp_uid, biway_pipe_chain=pipe_script)

    display_output("target uid: [" + ifp_entity.target_uid + ']')
    display_output("setup pipe...")
    ifp_transaction(ser,
                    gen_host_command('plc_package',ifp_entity.gen_setup_frame()),
                    ifp_entity.calc_timeout())

    display_output("sync...")
    ifp_transaction(ser,
                    gen_host_command('plc_package',ifp_entity.gen_sync_frame()),
                    ifp_entity.calc_timeout())

    display_output("erase user array...")
    ifp_app_transaction(ser,
                        gen_host_command('plc_package',ifp_entity.gen_erase_usercode_frame()),
                        ifp_entity.calc_timeout())
    
    display_output("upload code...")
    for [start, end] in data_chips:
        while(start<end):
            if (end - start < MAX_APP_LOAD):
                load = data_buffer[start:end]
##                display_output('start:%d'%start, 'end:%d'%end, dec2hexstr(load))
            else:
                load = data_buffer[start: (start+MAX_APP_LOAD)]
##                display_output('start:%d'%start, 'end:%d'%(start+MAX_APP_LOAD), dec2hexstr(load))

            ifp_app_transaction(ser,
                                gen_host_command('plc_package',ifp_entity.gen_prgm_usercode_frame(start,dec2str(load))),
                                ifp_entity.calc_timeout())
            start = start + len(load)
            response_others()

    display_output("reset target node...")
    ifp_app_transaction(ser,
                        gen_host_command('plc_package',ifp_entity.gen_reset_node_frame()),
                        ifp_entity.calc_timeout())
    
    display_output("upload successfully")

def pipe_trim(s):
    s = nospace(s)
    if len(s)==12:
        return s+'2020'
    elif len(s)%16 == 0:
        return s
    else:
        raise SyntaxError(s)


def process_pipe_info(pipe_info_text):
    
    pipe_info_text = pipe_info_text.split('\n')
    
    line_num = 0
    pipe_set = []
    for line in pipe_info_text:
        line_num += 1
        if line.find('#') < 0:
            s = nospace(line)
        else:
            s = nospace(line[0:line.find('#')])
        try:
            if(len(s)>0):
                pipe_set.append(pipe_trim(s))
        except SyntaxError:
            display_output("line %d, error format:" % line_num, line)
            raise SyntaxError(line)
    return pipe_set

def read_pipe_file(filepath):
    ''' Read a txt file named 'targets.txt' located in the same dictionary

        A file named 'targets.txt' is formatted like this:

            # comment

            # normal 1-stage pipe, node [5e1d0a048822] is the target
            5e1d0a048822 2020

            # normal 2-stage pipe, node [5e1d0a048611] is the target, node [5e1d0a048822] is the routing node
            5e1d0a048822 2020 5e1d0a048611 2020

            # just uid, a default '5e1d0a056699 2020' pipe will setup
            5e1d0a056699
        
        Returns:
            a pipe description sequence
    '''

    with open(filepath) as f:
        pipe_set = process_pipe_info(f.read())
        
    return pipe_set
    

    
def batch_burn_process(port, ifpp_uid, pipe_set, data_buffer, data_chips):
    with uart_env(port) as ser:
        okay_set=[]
        fail_set=[]
        time_start = time.clock()
        for pipe in pipe_set:
            try:
                ifp_burn(ser,ifpp_uid, pipe, data_buffer, data_chips)
                okay_set.append(pipe[-16:-4])
            except IfpException as ie:
                display_output('IfpException:%s' % ie.args[0])
                display_output("upload fail, abort it")
                fail_set.append(pipe[-16:-4])
    display_output("=======================")
    display_output("*      Reports        *")
    display_output("-----------------------")
    display_output("IFP Burn Success Nodes:")
    for uid in okay_set:
        display_output(uid)
    display_output("-----------------------")

    if len(fail_set)>0:
        display_output("IFP Burn Fail Nodes:")
        for uid in fail_set:
            display_output(uid)
        display_output("-----------------------")
    display_output("Total cost %.2f seconds" % (time.clock()-time_start))
    
    
def main():
    '''Usage:
    1. ifp.exe hexfile_path
        a file named "targets.txt" located in the same dictonary is used as the pipe description file.
        below is a example of "targets.txt":

            # '#' means comment

            # normal 1-stage pipe, node [5e1d0a048822] is the target
            5e1d0a048822 2020 # inline comment

            # normal 2-stage pipe, node [5e1d0a048611] is the target, node [5e1d0a048822] is the routing node
            5e1d0a048822 2020 5e1d0a048611 2020

            # just uid, a default '5e1d0a056699 2020' pipe will setup
            5e1d0a056699

    2. ifp.exe hexfile_path [pipe1] [pipe2] ...
        * when hexfile_path or pipe string contains space character, it should be surrounded by ""

Examples:
    ifp.exe meter.hex

    ifp.exe meter.hex 5e1d0a051122

    ifp.exe "e:\my work\hex\meter.hex"

    ifp.exe meter.hex 5e1d0a0511222080

    ifp.exe meter.hex "5e1d0a051122 2080"

    ifp.exe meter.hex "5e1d0a051122 2080" "5e1d0a051122 2080 5e1d0a048822 4040"

Author:
    Lv Haifeng(machael.lv@qq.com)
    2015-12-25
    '''

    if len(sys.argv)==1:
        display_output(sys.modules['__main__'].main.__doc__)
        return
    elif len(sys.argv)==2:
        data_buffer, data_chips = readhexfile(sys.argv[1])
        pipe_set = read_pipe_file('targets.txt')
    else:
        data_buffer, data_chips = readhexfile(sys.argv[1])
        pipe_set = []
        for pipe in sys.argv[2:]:
            pipe_set.append(pipe_trim(pipe))

    ## get com, ifpp information
    while(True):
        try:
            f = open('ifp.cfg','rb')
            config = pickle.load(f)
            port = config['port']
            f.close()

            ser = init_uart(port)
            ifpp_uid = check_ifpp(ser)
            if(ifpp_uid != ''):
                ser.close()
                break
            else:
                port = raw_input("can't connect IFPP by %s, reinput com port\n>" % port)
        except SerialException:
            port = raw_input("can't open %s, reinput com port\n>" % port)
        except IOError:
            port = raw_input('input IFPP com port, e.g. com2\n>')
        finally:
            f = open('ifp.cfg','wb')
            config = {'port':port}
            pickle.dump(config,f)
            f.close()

    ## burn process
    batch_burn_process(port, ifpp_uid, pipe_set, data_buffer, data_chips)

if __name__ == "__main__":
##    port = 'com2'
##    uid = '5e1d0a085566'
##    filepath = r'E:\Works\PLC_G1_Project\FirmWare\powermesh_unify\device_mt\branch_optimize_terminal\output\powermesh_mt.hex';
##    pipe = '5E1D0A087176 2020 0B9A090A272D 2020'
##
##    with uart_env('com2') as ser:
##        if ser != None:
##            try:
##                ifpp_uid = check_ifpp(ser)
##                display_output('IFPP UID:',ifpp_uid)
##
##                data_buffer, data_chips = readhexfile(r'e:\temp\057.BL6810ModuleQC\qc.hex')
##                ifp_burn(ser,ifpp_uid ,pipe ,data_buffer ,data_chips)
##            except IfpException:
##                display_output(IfpException)

    #sys.argv =[sys.argv[0],'qc.hex','234565446544','5e1d0a087176']
    #sys.argv =[sys.argv[0],'qc.hex']
    #sys.argv =[sys.argv[0],r'e:\Works\PLC_G1_Project\FirmWare\PLC1G\075.Simple2\simple.hex','5e1d0a087176']
    main()                
