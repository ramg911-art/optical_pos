import React, { useEffect, useState } from "react"
import axios from "axios"

import {
  Container,
  Title,
  TextInput,
  Button,
  Table,
  Card,
  Group
} from "@mantine/core"

const API = "http://192.168.10.216:9200"

export default function Suppliers(){

  const token = localStorage.getItem("token")

  const headers = {
    Authorization:`Bearer ${token}`
  }

  const [suppliers,setSuppliers] = useState<any[]>([])

  const [name,setName] = useState("")
  const [phone,setPhone] = useState("")
  const [email,setEmail] = useState("")
  const [address,setAddress] = useState("")

  // ================= LOAD SUPPLIERS =================
  const loadSuppliers = async ()=>{

    try{

      const res = await axios.get(
        `${API}/suppliers/`,
        {headers}
      )

      setSuppliers(res.data)

    }catch(err){
      console.error(err)
      alert("Failed to load suppliers")
    }
  }

  // load on start
  useEffect(()=>{
    loadSuppliers()
  },[])

  // ================= ADD SUPPLIER =================
  const addSupplier = async ()=>{

    if(!name){
      alert("Supplier name required")
      return
    }

    try{

      await axios.post(
        `${API}/suppliers/`,
        {
          name,
          phone,
          email,
          address
        },
        {headers}
      )

      // reload list
      loadSuppliers()

      // clear form
      setName("")
      setPhone("")
      setEmail("")
      setAddress("")

    }catch(err){
      console.error(err)
      alert("Failed to add supplier")
    }
  }

  // ================= UI =================
  return(

    <Container size="lg">

      <Title mb="md">Suppliers</Title>

      <Card shadow="sm" p="md" mb="lg">

        <Group grow>

          <TextInput
            label="Name"
            value={name}
            onChange={(e)=>setName(e.target.value)}
          />

          <TextInput
            label="Phone"
            value={phone}
            onChange={(e)=>setPhone(e.target.value)}
          />

          <TextInput
            label="Email"
            value={email}
            onChange={(e)=>setEmail(e.target.value)}
          />

        </Group>

        <TextInput
          mt="sm"
          label="Address"
          value={address}
          onChange={(e)=>setAddress(e.target.value)}
        />

        <Button
          mt="md"
          onClick={addSupplier}
        >
          Add Supplier
        </Button>

      </Card>


      <Card shadow="sm" p="md">

        <Table>

          <thead>
            <tr>
              <th>Name</th>
              <th>Phone</th>
              <th>Email</th>
              <th>Address</th>
            </tr>
          </thead>

          <tbody>

            {suppliers.map((s:any)=>(
              <tr key={s.id}>
                <td>{s.name}</td>
                <td>{s.phone}</td>
                <td>{s.email}</td>
                <td>{s.address}</td>
              </tr>
            ))}

          </tbody>

        </Table>

      </Card>

    </Container>

  )
}
