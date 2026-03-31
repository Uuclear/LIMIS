<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import {
  getUserList, createUser, updateUser, deleteUser,
  resetPassword, toggleUserActive, kickoutUserSessions, getRoleList,
} from '@/api/system'

interface UserRow {
  id: number
  username: string
  real_name: string
  phone: string
  email: string
  department: string
  roles: { id: number; name: string }[]
  is_active: boolean
  created_at: string
}

const loading = ref(false)
const tableData = ref<UserRow[]>([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 20, username: '', real_name: '', department: '' })

const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref()
const roleOptions = ref<{ id: number; name: string }[]>([])

const form = reactive({
  id: 0,
  username: '',
  real_name: '',
  phone: '',
  email: '',
  department: '',
  role_ids: [] as number[],
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
}

const pwdDialogVisible = ref(false)
const pwdForm = reactive({ id: 0, new_password: '' })

const userStore = useUserStore()
const currentUserId = computed(() => {
  const u = userStore.userInfo as Record<string, unknown> | null
  if (!u) return undefined
  return (u.id as number | undefined) ?? (u.userId as number | undefined)
})
function isSelf(row: UserRow) {
  return currentUserId.value !== undefined && row.id === currentUserId.value
}

async function handleKickoutSessions(row: UserRow) {
  if (isSelf(row)) {
    ElMessage.warning('不能踢出当前登录账号')
    return
  }
  await ElMessageBox.confirm('确认将该用户所有会话踢下线？', '提示', { type: 'warning' })
  await kickoutUserSessions(row.id)
  ElMessage.success('已踢下线')
}

async function fetchList() {
  loading.value = true
  try {
    const res: any = await getUserList(query)
    tableData.value = res.results ?? res.list ?? []
    total.value = res.total ?? res.count ?? 0
  } finally {
    loading.value = false
  }
}

async function fetchRoles() {
  const res: any = await getRoleList({ page_size: 200 })
  roleOptions.value = res.results ?? res.list ?? []
}

function handleSearch() {
  query.page = 1
  fetchList()
}

function handleReset() {
  Object.assign(query, { page: 1, username: '', real_name: '', department: '' })
  fetchList()
}

function openCreate() {
  dialogTitle.value = '新增用户'
  Object.assign(form, {
    id: 0, username: '', real_name: '', phone: '',
    email: '', department: '', role_ids: [], password: '',
  })
  dialogVisible.value = true
}

function openEdit(row: UserRow) {
  dialogTitle.value = '编辑用户'
  const r = row as any
  Object.assign(form, {
    id: row.id,
    username: row.username,
    real_name: r.real_name || [r.first_name, r.last_name].filter(Boolean).join(' ') || '',
    phone: row.phone ?? '',
    email: row.email ?? '',
    department: row.department ?? '',
    role_ids: (row.roles ?? []).map(r => r.id),
    password: '',
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value?.validate()
  if (form.id) {
    await updateUser(form.id, {
      real_name: form.real_name,
      phone: form.phone,
      email: form.email,
      department: form.department,
      role_ids: form.role_ids,
    })
    ElMessage.success('更新成功')
  } else {
    await createUser({
      username: form.username,
      password: form.password,
      real_name: form.real_name,
      phone: form.phone,
      email: form.email,
      department: form.department,
      role_ids: form.role_ids,
    })
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  fetchList()
}

async function handleDelete(row: UserRow) {
  await ElMessageBox.confirm('确认删除该用户？', '提示', { type: 'warning' })
  await deleteUser(row.id)
  ElMessage.success('删除成功')
  fetchList()
}

async function handleToggleActive(row: UserRow) {
  const action = row.is_active ? '禁用' : '启用'
  await ElMessageBox.confirm(`确认${action}该用户？`, '提示', { type: 'warning' })
  await toggleUserActive(row.id)
  ElMessage.success(`${action}成功`)
  fetchList()
}

function openResetPwd(row: UserRow) {
  pwdForm.id = row.id
  pwdForm.new_password = ''
  pwdDialogVisible.value = true
}

async function handleResetPwd() {
  if (!pwdForm.new_password) return ElMessage.warning('请输入新密码')
  await resetPassword(pwdForm.id, { password: pwdForm.new_password })
  ElMessage.success('密码重置成功')
  pwdDialogVisible.value = false
}

onMounted(() => { fetchList(); fetchRoles() })
</script>

<template>
  <div class="page-container">
    <el-card shadow="never">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="用户名">
          <el-input v-model="query.username" placeholder="请输入" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="query.real_name" placeholder="请输入" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="query.department" placeholder="请输入" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>用户列表</span>
          <el-button v-permission="'system:create'" type="primary" :icon="Plus" @click="openCreate">新增用户</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column label="姓名" min-width="100">
          <template #default="{ row }">
            {{ (row as any).realName || (row as any).real_name || (row as any).firstName || (row as any).first_name || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="手机号" min-width="130">
          <template #default="{ row }">{{ (row as any).phone || '—' }}</template>
        </el-table-column>
        <el-table-column label="部门" min-width="120">
          <template #default="{ row }">{{ (row as any).department || '—' }}</template>
        </el-table-column>
        <el-table-column label="角色" min-width="160">
          <template #default="{ row }">
            <el-tag v-for="role in row.roles" :key="role.id" size="small" style="margin: 2px">
              {{ role.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="340" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'system:edit'" link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button v-permission="'system:edit'" link type="primary" @click="openResetPwd(row)">重置密码</el-button>
            <el-tooltip :disabled="!isSelf(row)" content="不能踢出当前登录账号" placement="top">
              <span style="display: inline-block; vertical-align: middle">
                <el-button
                  v-permission="'system:edit'"
                  link
                  type="warning"
                  :disabled="isSelf(row)"
                  @click="handleKickoutSessions(row)"
                >踢下线</el-button>
              </span>
            </el-tooltip>
            <el-button v-permission="'system:edit'" link :type="row.is_active ? 'warning' : 'success'" @click="handleToggleActive(row)">
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button v-permission="'system:delete'" link type="danger" @click="handleDelete(row)">删除</el-button>
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

    <!-- Create / Edit dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="560px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="!!form.id" />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="form.department" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role_ids" multiple placeholder="请选择角色" style="width: 100%">
            <el-option v-for="r in roleOptions" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!form.id" label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button v-permission="form.id ? 'system:edit' : 'system:create'" type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Reset password dialog -->
    <el-dialog v-model="pwdDialogVisible" title="重置密码" width="420px" destroy-on-close>
      <el-form label-width="80px">
        <el-form-item label="新密码">
          <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialogVisible = false">取消</el-button>
        <el-button v-permission="'system:edit'" type="primary" @click="handleResetPwd">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
