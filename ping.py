import asyncio
import sys
import mtrpacket

# https://raw.githubusercontent.com/matt-kimball/mtr-packet-python/master/examples/ping.py
#
#  We send the probe in a coroutine since mtrpacket operates
#  asynchronously.  In a more complicated program, this
#  allows other asynchronous operations to occur concurrently
#  with the probe.
#
async def probe(host):
    async with mtrpacket.MtrPacket() as mtr:
        try:
            result = await mtr.probe(host)
        except asyncio.CancelledError:
            print(f'task timeout {host}')
            return
        #  If the ping got a reply, report the IP address and time
        if result.success:
            print('reply from {} in {} ms'.format(
                result.responder, result.time_ms))
        else:
            print('no reply ({})'.format(result.result))

async def run(subnet, subnet_mask):
    tasks = [asyncio.create_task(probe(f'{subnet}.{i}')) for i in range(0, 254)]
    running_tasks = asyncio.shield(asyncio.gather(*tasks))
    try: 
        await asyncio.wait_for(running_tasks, 10)
    except asyncio.TimeoutError:
        print('some host names did not reply within 10s')


#  Get a hostname to ping from the commandline
if len(sys.argv) == 2:
    hostname = sys.argv[1]
    #  We need asyncio's event loop to run the coroutine
    loop = asyncio.get_event_loop()
    try:
        probe_coroutine = probe(hostname)
        try:
            loop.run_until_complete(probe_coroutine)
        except mtrpacket.HostResolveError:
            print("Can't resolve host '{}'".format(hostname))
    finally:
        loop.close()

# Ip address range given
elif len(sys.argv) == 3:
    subnet = '.'.join(sys.argv[1].split('.')[:-1])
    subnet_mask = sys.argv[2]
    # TODO: calc subnet format into ip address range
    asyncio.run(run(subnet, subnet_mask))

else:
    print('Usage: python3 ping.py <hostname>')
    sys.exit(1)



