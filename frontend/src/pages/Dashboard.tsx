import React, { useEffect, useState } from "react"
import axios from "axios"
import { useNavigate } from "react-router-dom"

import { Card, Button, SimpleGrid, Title, Text } from "@mantine/core"

export default function Dashboard(){

  const nav = useNavigate()
  const [data,setData]=useState<any>(null)

  useEffect(()=>{
    const fetchData = async () => {

      const res = await axios.get(
        "http://192.168.10.216:9200/dashboard/",
        {
          headers:{
            Authorization:`Bearer ${localStorage.getItem("token")}`
          }
        }
      )

      setData(res.data)
    }

    fetchData()
  },[])

  if(!data) return <h2>Loading dashboard...</h2>

  return (
    <div style={{padding:30}}>

      <Title order={2} mb="lg">
        Optical POS Dashboard
      </Title>

      {/* NAVIGATION CARDS */}
      <SimpleGrid cols={3} spacing="lg" mb="xl">

        <Card shadow="md" padding="lg">
          <Button fullWidth onClick={()=>nav("/sales")}>
            Billing
          </Button>
        </Card>

        <Card shadow="md" padding="lg">
          <Button fullWidth onClick={()=>nav("/items")}>
            Items
          </Button>
        </Card>

        <Card shadow="md" padding="lg">
          <Button fullWidth onClick={()=>nav("/suppliers")}>
            Suppliers
          </Button>
        </Card>

        <Card shadow="md" padding="lg">
          <Button fullWidth onClick={()=>nav("/lens")}>
            Lens Orders
          </Button>
        </Card>

        <Card shadow="md" padding="lg">
          <Button fullWidth onClick={()=>nav("/history")}>
            Sales History
          </Button>
        </Card>

      </SimpleGrid>

      {/* STATS */}
      <SimpleGrid cols={3} spacing="lg">

        <Card shadow="sm">
          <Text>Sales Today</Text>
          <Title order={3}>₹ {data.sales_today}</Title>
        </Card>

        <Card shadow="sm">
          <Text>Bills</Text>
          <Title order={3}>{data.sales_count}</Title>
        </Card>

        <Card shadow="sm">
          <Text>Low Stock</Text>
          <Title order={3}>{data.low_stock_items}</Title>
        </Card>

        <Card shadow="sm">
          <Text>Pending Orders</Text>
          <Title order={3}>{data.pending_lens_orders}</Title>
        </Card>

        <Card shadow="sm">
          <Text>Ready Orders</Text>
          <Title order={3}>{data.ready_orders}</Title>
        </Card>

        <Card shadow="sm">
          <Text>Purchases</Text>
          <Title order={3}>₹ {data.purchase_today}</Title>
        </Card>

      </SimpleGrid>

    </div>
  )
}
