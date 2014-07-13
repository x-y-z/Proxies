#!/usr/bin/python
"""
source: http://code.activestate.com/recipes/114642/

usage 'pinhole port host [newport]'

Pinhole forwards the port to the host specified.
The optional newport parameter may be used to
redirect to a different port.

eg. pinhole 80 webserver
    Forward all incoming WWW sessions to webserver.

    pinhole 23 localhost 2323
    Forward all telnet sessions to port 2323 on localhost.
"""

import sys
from socket import *
from threading import Thread
import time
from proxy_retriever import ProxyRetriever

LOGGING = 1

def log( s ):
    if LOGGING:
        print '%s:%s' % ( time.ctime(), s )
        sys.stdout.flush()

class PipeThread( Thread ):
    pipes = []
    def __init__( self, source, sink ):
        Thread.__init__( self )
        self.source = source
        self.sink = sink

        log( 'Creating new pipe thread  %s ( %s -> %s )' % \
            ( self, source.getpeername(), sink.getpeername() ))
        PipeThread.pipes.append( self )
        log( '%s pipes active' % len( PipeThread.pipes ))

    def run( self ):
        while 1:
            try:
                data = self.source.recv( 1024 )
                if not data: break
                self.sink.send( data )
            except:
                break

        log( '%s terminating' % self )
        PipeThread.pipes.remove( self )
        log( '%s pipes active' % len( PipeThread.pipes ))

class Pinhole( Thread ):
    def __init__( self, port):
        Thread.__init__( self )
        self.proxy_retriever = ProxyRetriever(True)
        newhost, newport = self.proxy_retriever.getAProxy()
        log( 'Redirecting: localhost:%s -> %s:%s' % ( port, newhost, newport ))
        self.newhost = newhost
        self.newport = newport
        self.sock = socket( AF_INET, SOCK_STREAM )
        self.sock.bind(( '', port ))
        self.sock.listen(5)
        self.running = True

    def run( self ):
        while self.running:
            newsock, address = self.sock.accept()
            log( 'Creating new session for %s %s ' % address )
            #fwd = socket( AF_INET, SOCK_STREAM )
            while 1:
                try:
                    fwd = create_connection(( self.newhost, self.newport ), 1)
                except socket.timeout:
                    newhost, newport = self.proxy_retriever.getAProxy()
                    self.newhost = newhost
                    self.newport = newport
                    continue
                except Exception as e:
                    print e
                    self.sock.close()
                    self.running = False
                break

            if not self.running:
                break

            PipeThread( newsock, fwd ).start()
            PipeThread( fwd, newsock ).start()

if __name__ == '__main__':


    #import sys
    #sys.stdout = open( 'pinhole.log', 'w' )

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("--local-port", type="int", action="store", default=7890,\
            help="Specify local port(default:7890) this program will listen")

    options, args = parser.parse_args()

    if options.local_port:
        port = options.local_port
        t = Pinhole(port)
        t.daemon = True
        print 'Starting Proxy...'
        t.start()
        try:
            while t.isAlive():
                t.join(1)
        except KeyboardInterrupt:
            print "^C is caught, exiting"
