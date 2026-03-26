<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getRoleList, createRole, updateRole, deleteRole, getPermissionList } from '@/api/system'

interface RoleRow {
  id: number
  name: string
  code: string
  description: string
  user_count: number
  permissions: number[]
}

interface PermNode {
  id: number
  name: string
  code: string
  children?: PermNode[]
}

const loading = ref(false)
const tableData = ref<RoleRow[]>([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 20 })

const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref()
const treeRef = ref()
const permTree = ref<PermNode[]>([])

const form = reactive({ id: 0, name: '', code: '', description: '', permission_ids: [] as number[] })

const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }],
}

async function fetchList() {
  loading.value = true
  try {
    const res: any = await getRoleList(query)
    tableData.value = res.results ?? res.list ?? []
    total.value = res.total ?? res.count ?? 0
  } finally {
    loading.value = false
  }
}

async function fetchPermissions() {
  const res: any = await getPermissionList({ page_size: 500 })
  permTree.value = buildTree(res.results ?? res.list ?? res ?? [])
}

function buildTree(list: any[]): PermNode[] {
  const map = new Map<number, PermNode>()
  const roots: PermNode[] = []
  for (const item of list) {
    map.set(item.id, { ...item, children: [] })
  }
  for (const item of list) {
    const node = map.get(item.id)!
    if (item.parent_id && map.has(item.parent_id)) {
      map.get(item.parent_id)!.children!.push(node)
    } else {
      roots.push(node)
    }
  }
  return roots
}

function openCreate() {
  dialogTitle.value = '新增角色'
  Object.assign(form, { id: 0, name: '', code: '', description: '', permission_ids: [] })
  dialogVisible.value = true
  setTimeout(() => treeRef.value?.setCheckedKeys([]), 0)
}

function openEdit(row: RoleRow) {
  dialogTitle.value = '编辑角色'
  Object.assign(form, { ...row, permission_ids: row.permissions ?? [] })
  dialogVisible.value = true
  setTimeout(() => treeRef.value?.setCheckedKeys(form.permission_ids), 0)
}

async function handleSubmit() {
  await formRef.value?.validate()
  const checkedKeys = treeRef.value?.getCheckedKeys(false) ?? []
  const halfKeys = treeRef.value?.getHalfCheckedKeys() ?? []
  const data = { ...form, permission_ids: [...checkedKeys, ...halfKeys] }

  if (form.id) {
    await updateRole(form.id, data)
    ElMessage.success('更新成功')
  } else {
    await createRole(data)
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  fetchList()
}

async function handleDelete(row: RoleRow) {
  await ElMessageBox.confirm('确认删除该角色？', '提示', { type: 'warning' })
  await deleteRole(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

onMounted(() => { fetchList(); fetchPermissions() })
</script>

<template>
  <div class="page-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>角色管理</span>
          <el-button type="primary" :icon="Plus" @click="openCreate">新增角色</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column prop="name" label="角色名称" min-width="140" />
        <el-table-column prop="code" label="角色编码" min-width="140" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="user_count" label="用户数" width="100" align="center" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total > 0"
        style="margin-top: 16px; justify-content: flex-end"
        background
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        :page-size="query.page_size"
        :current-page="query.page"
        :page-sizes="[20, 50, 100]"
        @current-change="(p: number) => { query.page = p; fetchList() }"
        @size-change="(s: number) => { query.page_size = s; query.page = 1; fetchList() }"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="form.code" :disabled="!!form.id" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="权限">
          <el-tree
            ref="treeRef"
            :data="permTree"
            show-checkbox
            node-key="id"
            :props="{ label: 'name', children: 'children' }"
            default-expand-all
            style="width: 100%; border: 1px solid var(--el-border-color); border-radius: 4px; padding: 8px"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
