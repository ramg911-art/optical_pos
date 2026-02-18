import React, { useEffect, useState } from "react"
import axios from "axios"
import {
  Container,
  Title,
  TextInput,
  Button,
  Table,
  Card,
  Group,
} from "@mantine/core"

const API = "http://192.168.10.216:9200"

export default function Categories() {

  const token = localStorage.getItem("token")
  const headers = { Authorization: `Bearer ${token}` }

  const [categories, setCategories] = useState<any[]>([])
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [editing, setEditing] = useState<any | null>(null)

  const loadCategories = async () => {
    const res = await axios.get(`${API}/categories/`, { headers })
    setCategories(res.data)
  }

  useEffect(() => {
    loadCategories()
  }, [])

  const createCategory = async () => {
    if (!name) {
      alert("Category name is required")
      return
    }

    await axios.post(
      `${API}/categories/`,
      { name, description },
      { headers },
    )

    setName("")
    setDescription("")
    loadCategories()
  }

  const saveCategory = async () => {
    if (!editing) return

    await axios.put(
      `${API}/categories/${editing.id}`,
      {
        name: editing.name,
        description: editing.description,
      },
      { headers },
    )

    setEditing(null)
    loadCategories()
  }

  const deleteCategory = async (id: number) => {
    if (!window.confirm("Delete this category?")) return

    await axios.delete(`${API}/categories/${id}`, { headers })
    loadCategories()
  }

  return (
    <Container size="lg">

      <Title mb="md">Categories</Title>

      <Card shadow="sm" p="md" mb="lg">

        <Group grow>
          <TextInput
            label="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <TextInput
            label="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </Group>

        <Button mt="md" onClick={createCategory}>
          Add Category
        </Button>

      </Card>

      <Card shadow="sm" p="md">

        <Table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th>Created</th>
              <th></th>
            </tr>
          </thead>
          <tbody>

            {categories.map((c: any) => (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td>{c.description}</td>
                <td>{c.created_at ? new Date(c.created_at).toLocaleDateString() : ""}</td>
                <td>
                  <Button
                    size="xs"
                    variant="light"
                    mr="xs"
                    onClick={() => setEditing({ ...c })}
                  >
                    Edit
                  </Button>
                  <Button
                    size="xs"
                    color="red"
                    variant="light"
                    onClick={() => deleteCategory(c.id)}
                  >
                    Delete
                  </Button>
                </td>
              </tr>
            ))}

          </tbody>
        </Table>

      </Card>

      {editing && (
        <Card shadow="sm" p="md" mt="lg">
          <Title order={4} mb="sm">Edit Category</Title>

          <Group grow>
            <TextInput
              label="Name"
              value={editing.name}
              onChange={(e) => setEditing({ ...editing, name: e.target.value })}
            />
            <TextInput
              label="Description"
              value={editing.description || ""}
              onChange={(e) => setEditing({ ...editing, description: e.target.value })}
            />
          </Group>

          <Group mt="md">
            <Button onClick={saveCategory}>
              Save
            </Button>
            <Button variant="default" onClick={() => setEditing(null)}>
              Cancel
            </Button>
          </Group>
        </Card>
      )}

    </Container>
  )
}

