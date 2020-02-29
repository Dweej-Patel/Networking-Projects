Dweej Patel
UNI: dp3039
Part 2 of Programming Assignment 1

My implementation of the proxy server:

    It is a simple proxy that reroutes requests appended to URL.

    Handling 301 requests: Checked if the response from server includes a 301 code.
                           If 301 code then resend request to Location URI included
                           in the header.
    
    Handling 404 requests: Try to look for the Referer header and try to receive a response
                           by sending another request to server using referer URI. If another
                           404 request is encountered just redirect the 404 to the client.
    
    Caching files: Cache files to the working directory where your proxy code is. If the file has
                   been cached just send the cached file to client. If file is not cached then
                   send request to server and cache the received body if code is 200.

    Side note: I will coninuously check readability and if readable we will continue with proccessing for 
               receiving from server or client. I also implemented a timer mechanism where if not readable 
               in allocated time I will just move on to proccessing.
    
**EXTRA CREDIT** 

    Implemented both the favicon.ico and mutithreading.

    favicon.ico: Maintained a queue to store domains associated with index.html file.
                 When a favicon.ico is encountered pop the domain from the queue and
                 request the favicon.ico file from the popped domain.

    Multithreading: Used the threading module that comes with python. Everytime a client
                    is accepted create a new thread to proccess that client. (I print to 
                    terminal when a new thread is created and when a thread ends.) The 
                    new thread is called on the workmythread function I implemented so 
                    that all client proccesses are controled by the function. I also implemented
                    thread locking for writing files to cache. I will lock threads when 
                    one thread is writing and another thread is concurrently tring to check if 
                    the file exists. Please check output in terminal that will indicate the 
                    current proccesses and accociated threads.
