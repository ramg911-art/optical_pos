import React from "react"
import { BrowserRouter, Routes, Route } from "react-router-dom"

import Login from "./pages/Login"
import Dashboard from "./pages/Dashboard"
import Items from "./pages/Items"
import Sales from "./pages/Sales"
import SalesHistory from "./pages/SalesHistory"
import LensOrders from "./pages/LensOrders"
import Suppliers from "./pages/Suppliers"

import Layout from "./components/Layout"

export default function App() {

  return (
    <BrowserRouter>

      <Routes>

        {/* LOGIN */}
        <Route path="/" element={<Login />} />

        {/* APP WITH NAVBAR */}
        <Route path="/dashboard" element={<Layout><Dashboard/></Layout>} />
        <Route path="/items" element={<Layout><Items/></Layout>} />
        <Route path="/sales" element={<Layout><Sales/></Layout>} />
        <Route path="/history" element={<Layout><SalesHistory/></Layout>} />
        <Route path="/lens" element={<Layout><LensOrders/></Layout>} />
        <Route path="/suppliers" element={<Layout><Suppliers/></Layout>} />

      </Routes>

    </BrowserRouter>
  )
}
