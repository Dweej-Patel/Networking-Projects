Dweej Patel
UNI: dp3039
Part 2 of Programming Assignment 1

My implementation of the proxy server:

    It is a simple proxy that reroutes requests appended to URL.

    Handling 301 requests: Checked if the response from the server includes a 301 code.
                           If 301 code then resend the request to Location URI included
                           in the header.
    
    Handling 404 requests: Try to look for the Referer header and try to receive a response
                           by sending another request to the server using referer URI. If another
                           404 request is encountered just redirect the 404 to the client.
    
    Caching files: Cache files to the working directory where your proxy code is. If the file has
                   been cached just send the cached file to the client. If the file is not cached then
                   send a request to the server and cache the received body if code is 200.

    Side note: I will continuously check readability and if readable we will continue with processing for 
               receiving from the server or client. I also implemented a timer mechanism where if not readable 
               in allocated time I will just move on to processing.
    
**EXTRA CREDIT** 

    Implemented both the favicon.ico and multithreading.

    favicon.ico: Maintained a queue to store domains associated with index.html file.
                 When a favicon.ico is encountered pop the domain from the queue and
                 request the favicon.ico file from the popped domain.

    Multithreading: Used the threading module that comes with python. Every time a client
                    is accepted to create a new thread to process that client. (I print to 
                    the terminal when a new thread is created and when a thread ends.) The 
                    new thread is called on the workmythread function I implemented so 
                    that all client processes are controlled by the function. I also implemented
                    thread locking for writing files to cache. I will lock threads when 
                    one thread is writing and another thread is concurrently trying to check if 
                    the file exists. Please check the output in the terminal that will indicate the 
                    current processes and associated threads.
