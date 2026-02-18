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
  const [purchasePrice,setPurchasePrice]=useState("")
  const [gstPercent,setGstPercent]=useState("")
  const [stock,setStock]=useState("")
  const [category,setCategory]=useState("")
  const [supplierName,setSupplierName]=useState("")
  const [supplierGst,setSupplierGst]=useState("")
  const [supplierContact,setSupplierContact]=useState("")
  const [supplierAddress,setSupplierAddress]=useState("")
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
    purchase_price: purchasePrice ? parseFloat(purchasePrice) : null,
    gst_percent: gstPercent ? parseFloat(gstPercent) : null,
    stock_qty: parseInt(stock || "0"),
    supplier_name: supplierName || null,
    supplier_gst: supplierGst || null,
    supplier_contact: supplierContact || null,
    supplier_address: supplierAddress || null,
  },
  { headers })

  setName("")
  setPrice("")
  setPurchasePrice("")
  setGstPercent("")
  setStock("")
  setCategory("")
  setSupplierName("")
  setSupplierGst("")
  setSupplierContact("")
  setSupplierAddress("")

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
      <div style={{marginTop:20, display:"grid", gridTemplateColumns:"repeat(2, minmax(0, 1fr))", gap:12}}>

        <div>
          <h3>Item Details</h3>
          <div style={{display:"flex", flexDirection:"column", gap:8}}>
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
              placeholder="Selling Price"
              value={price}
              onChange={e=>setPrice(e.target.value)}
            />

            <input
              placeholder="Purchase Price"
              value={purchasePrice}
              onChange={e=>setPurchasePrice(e.target.value)}
            />

            <input
              placeholder="GST %"
              value={gstPercent}
              onChange={e=>setGstPercent(e.target.value)}
            />

            <input
              placeholder="HSN Code"
              // we don't store this in local state for add form separately;
              // can be extended later if needed
              onChange={()=>{}}
            />

            <input
              placeholder="Stock"
              value={stock}
              onChange={e=>setStock(e.target.value)}
            />
          </div>
        </div>

        <div>
          <h3>Supplier Details</h3>
          <div style={{display:"flex", flexDirection:"column", gap:8}}>
            <input
              placeholder="Supplier Name"
              value={supplierName}
              onChange={e=>setSupplierName(e.target.value)}
            />
            <input
              placeholder="Supplier GST"
              value={supplierGst}
              onChange={e=>setSupplierGst(e.target.value)}
            />
            <input
              placeholder="Supplier Contact"
              value={supplierContact}
              onChange={e=>setSupplierContact(e.target.value)}
            />
            <textarea
              placeholder="Supplier Address"
              value={supplierAddress}
              onChange={e=>setSupplierAddress(e.target.value)}
              rows={3}
            />
            <button onClick={addItem}>
              Add Item
            </button>
          </div>
        </div>
      </div>

      {/* TABLE */}
      <table border={1} cellPadding={8} style={{marginTop:20, width:"100%", borderCollapse:"collapse"}}>
        <thead>
          <tr>
            <th>Name</th>
            <th>Selling Price</th>
            <th>Purchase Price</th>
            <th>GST %</th>
            <th>HSN</th>
            <th>Supplier</th>
            <th>Stock</th>
            <th></th>
          </tr>
        </thead>

        <tbody>
          {filtered.map(i=>(
            <tr key={i.id}>
              <td>{i.name}</td>
              <td>{i.selling_price}</td>
              <td>{i.purchase_price}</td>
              <td>{i.gst_percent}</td>
              <td>{i.hsn_code}</td>
              <td>{i.supplier_name}</td>
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
            placeholder="Purchase Price"
            value={edit.purchase_price ?? ""}
            onChange={e=>setEdit({
              ...edit,
              purchase_price: e.target.value ? Number(e.target.value) : null
            })}
          />

          <input
            placeholder="GST %"
            value={edit.gst_percent ?? ""}
            onChange={e=>setEdit({
              ...edit,
              gst_percent: e.target.value ? Number(e.target.value) : null
            })}
          />

          <input
            placeholder="HSN Code"
            value={edit.hsn_code ?? ""}
            onChange={e=>setEdit({
              ...edit,
              hsn_code: e.target.value || null
            })}
          />

          <input
            placeholder="Supplier Name"
            value={edit.supplier_name ?? ""}
            onChange={e=>setEdit({
              ...edit,
              supplier_name: e.target.value || null
            })}
          />

          <input
            placeholder="Supplier GST"
            value={edit.supplier_gst ?? ""}
            onChange={e=>setEdit({
              ...edit,
              supplier_gst: e.target.value || null
            })}
          />

          <input
            placeholder="Supplier Contact"
            value={edit.supplier_contact ?? ""}
            onChange={e=>setEdit({
              ...edit,
              supplier_contact: e.target.value || null
            })}
          />

          <textarea
            placeholder="Supplier Address"
            value={edit.supplier_address ?? ""}
            onChange={e=>setEdit({
              ...edit,
              supplier_address: e.target.value || null
            })}
            rows={3}
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
