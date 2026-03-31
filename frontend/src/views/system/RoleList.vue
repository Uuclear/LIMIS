<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getRoleList, createRole, updateRole, deleteRole, getPermissionGrouped } from '@/api/system'

interface RoleRow {
  id: number
  name: string
  code: string
  description: string
  user_count?: number
  permissions?: { id: number }[]
}

const loading = ref(false)
const tableData = ref<RoleRow[]>([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 20 })

const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref()

const form = reactive({
  id: 0,
  name: '',
  code: '',
  description: '',
  permission_ids: [] as number[],
})

const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }],
}

const grouped = ref<Record<string, any[]>>({})

const moduleTitle: Record<string, string> = {
  system: '系统管理',
  project: '工程项目',
  commission: '委托受理',
  testing: '检测管理',
  report: '报告管理',
  quality: '质量管理',
  equipment: '设备管理',
  consumables: '耗材管理',
  staff: '人员管理',
  standards: '标准规范',
  environment: '环境监控',
  sample: '样品管理',
}

const moduleKeys = computed(() => Object.keys(grouped.value).sort())

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
  const res: any = await getPermissionGrouped()
  grouped.value = res && typeof res === 'object' ? res : {}
}

function openCreate() {
  dialogTitle.value = '新增角色'
  Object.assign(form, {
    id: 0,
    name: '',
    code: '',
    description: '',
    permission_ids: [],
  })
  dialogVisible.value = true
}

function openEdit(row: RoleRow) {
  dialogTitle.value = '编辑角色'
  const ids = (row.permissions ?? []).map((p) => p.id)
  Object.assign(form, {
    id: row.id,
    name: row.name,
    code: row.code,
    description: row.description ?? '',
    permission_ids: ids,
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value?.validate()
  const payload = {
    name: form.name,
    code: form.code,
    description: form.description,
    permission_ids: form.permission_ids,
  }
  if (form.id) {
    await updateRole(form.id, payload)
    ElMessage.success('更新成功')
  } else {
    await createRole(payload)
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

onMounted(() => {
  fetchList()
  fetchPermissions()
})
</script>

<template>
  <div class="page-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>角色管理</span>
          <el-button v-permission="'system:create'" type="primary" :icon="Plus" @click="openCreate">新增角色</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="tableData" stripe border>
        <el-table-column prop="name" label="角色名称" min-width="140" />
        <el-table-column prop="code" label="角色编码" min-width="140" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="user_count" label="用户数" width="100" align="center" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'system:edit'" link type="primary" @click="openEdit(row)">编辑</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="720px" destroy-on-close>
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
          <el-scrollbar max-height="360px">
            <el-collapse>
              <el-collapse-item
                v-for="mod in moduleKeys"
                :key="mod"
                :title="moduleTitle[mod] || mod"
              >
                <el-checkbox-group v-model="form.permission_ids" class="perm-group">
                  <el-checkbox
                    v-for="p in grouped[mod]"
                    :key="p.id"
                    :label="p.id"
                  >
                    {{ p.name }}（{{ p.code }}）
                  </el-checkbox>
                </el-checkbox-group>
              </el-collapse-item>
            </el-collapse>
          </el-scrollbar>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button v-permission="form.id ? 'system:edit' : 'system:create'" type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.perm-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
}
</style>
