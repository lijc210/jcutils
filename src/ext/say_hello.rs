use pyo3::prelude::*;

#[pyfunction]
pub fn say_hello() {
    println!("Hello, world!");
}
