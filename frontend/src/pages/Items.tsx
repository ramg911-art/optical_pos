import React, { useEffect, useState } from "react"
import axios from "axios"

const API = "http://192.168.10.216:9200"

export default function Items(){

  const token = localStorage.getItem("token")
  const headers = { Authorization:`Bearer ${token}` }

  const [items,setItems]=useState<any[]>([])
  const [search,setSearch]=useState("")

  const [name,setName]=useState("")
  const [price,setPrice]=useState("")
  const [stock,setStock]=useState("")
  const [category,setCategory]=useState("")
  const [categories,setCategories]=useState<any[]>([])


  const [edit,setEdit]=useState<any>(null)

  const loadItems = async () => {
  const res = await axios.get(`${API}/items/`,{ headers })
  setItems(res.data)
}

const loadCategories = async () => {
  const res = await axios.get(`${API}/items/categories`,{ headers })
  setCategories(res.data)
}

useEffect(()=>{
  loadItems()
  loadCategories()
},[])


  // ---------- ADD ----------
 const addItem = async () => {

  if(!name || !category){
    alert("Name and Category required")
    return
  }

  await axios.post(`${API}/items/`,
  {
    name: name,
    category_id: parseInt(category),
    selling_price: parseFloat(price || "0"),
    stock_qty: parseInt(stock || "0")
  },
  { headers })

  setName("")
  setPrice("")
  setStock("")
  setCategory("")

  loadItems()
}


  // ---------- SAVE EDIT ----------
  const saveEdit = async () => {

    await axios.put(
      `${API}/items/${edit.id}`,
      edit,
      { headers }
    )

    setEdit(null)
    loadItems()
  }

  const filtered = items.filter(i =>
    i.name.toLowerCase().includes(search.toLowerCase())
  )

  return(
    <div style={{padding:40}}>

      <h1>Item Management</h1>

      {/* SEARCH */}
      <input
        placeholder="Search..."
        value={search}
        onChange={e=>setSearch(e.target.value)}
      />

      {/* ADD FORM */}
      <div style={{marginTop:20}}>

        <input
          placeholder="Name"
          value={name}
          onChange={e=>setName(e.target.value)}
        />

        <select
          value={category}
          onChange={e=>setCategory(e.target.value)}
        >

          <option value="">Select Category</option>

          {categories.map(c=>(
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}

        </select>



        <input
          placeholder="Price"
          value={price}
          onChange={e=>setPrice(e.target.value)}
        />

        <input
          placeholder="Stock"
          value={stock}
          onChange={e=>setStock(e.target.value)}
        />

        <button onClick={addItem}>
          Add Item
        </button>
      </div>

      {/* TABLE */}
      <table border={1} cellPadding={8} style={{marginTop:20}}>
        <thead>
          <tr>
            <th>Name</th>
            <th>Price</th>
            <th>Stock</th>
            <th></th>
          </tr>
        </thead>

        <tbody>
          {filtered.map(i=>(
            <tr key={i.id}>
              <td>{i.name}</td>
              <td>{i.selling_price}</td>
              <td>{i.stock_qty}</td>

              <td>
                <button onClick={()=>setEdit({...i})}>
                  Edit
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* EDIT PANEL */}
      {edit && (
        <div style={{marginTop:30}}>
          <h3>Edit Item</h3>

          <input
            value={edit.name}
            onChange={e=>setEdit({...edit,name:e.target.value})}
          />

          <input
            value={edit.selling_price}
            onChange={e=>setEdit({...edit,
              selling_price:Number(e.target.value)})
            }
          />

          <input
            value={edit.stock_qty}
            onChange={e=>setEdit({...edit,
              stock_qty:Number(e.target.value)})
            }
          />

          <button onClick={saveEdit}>
            Save
          </button>

          <button onClick={()=>setEdit(null)}>
            Cancel
          </button>
        </div>
      )}

    </div>
  )
}
