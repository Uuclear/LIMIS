<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getQualificationProfiles, createQualificationProfile, updateQualificationProfile } from '@/api/quality'
import { getStandardList } from '@/api/standards'
import { getTestMethods, getRecordTemplates } from '@/api/testing'

const loading = ref(false)
const profileList = ref<any[]>([])

const standards = ref<any[]>([])
const methods = ref<any[]>([])
const templates = ref<any[]>([])

const optionsLoading = ref(false)

async function fetchOptions() {
  optionsLoading.value = true
  try {
    const [stdRes, mRes, tRes]: any[] = await Promise.all([
      getStandardList({ page_size: 500 }),
      getTestMethods({ page_size: 500 }),
      getRecordTemplates({ page_size: 500 }),
    ])
    standards.value = stdRes.results ?? stdRes.list ?? stdRes ?? []
    methods.value = mRes.results ?? mRes.list ?? mRes ?? []
    templates.value = tRes.results ?? tRes.list ?? tRes ?? []
  } finally {
    optionsLoading.value = false
  }
}

async function fetchProfiles() {
  loading.value = true
  try {
    const res: any = await getQualificationProfiles({ page_size: 200 })
    profileList.value = res.results ?? res.list ?? res ?? []
  } finally {
    loading.value = false
  }
}

const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')

const form = reactive({
  id: 0,
  name: '',
  is_active: true,
  valid_from: '',
  valid_to: '',
  allowed_standards: [] as number[],
  allowed_test_methods: [] as number[],
  allowed_record_templates: [] as number[],
})

function openCreate() {
  dialogMode.value = 'create'
  Object.assign(form, {
    id: 0,
    name: '',
    is_active: true,
    valid_from: '',
    valid_to: '',
    allowed_standards: [],
    allowed_test_methods: [],
    allowed_record_templates: [],
  })
  dialogVisible.value = true
}

function openEdit(p: any) {
  dialogMode.value = 'edit'
  Object.assign(form, {
    id: p.id,
    name: p.name ?? '',
    is_active: p.is_active ?? true,
    valid_from: p.valid_from ?? '',
    valid_to: p.valid_to ?? '',
    allowed_standards: p.allowed_standards ?? [],
    allowed_test_methods: p.allowed_test_methods ?? [],
    allowed_record_templates: p.allowed_record_templates ?? [],
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入资质配置名称')
    return
  }
  const payload: any = {
    name: form.name,
    is_active: form.is_active,
    valid_from: form.valid_from || null,
    valid_to: form.valid_to || null,
    allowed_standards: form.allowed_standards,
    allowed_test_methods: form.allowed_test_methods,
    allowed_record_templates: form.allowed_record_templates,
  }
  if (dialogMode.value === 'create') {
    await createQualificationProfile(payload)
  } else {
    await updateQualificationProfile(form.id, payload)
  }
  ElMessage.success(dialogMode.value === 'create' ? '创建成功' : '更新成功')
  dialogVisible.value = false
  await fetchProfiles()
}

onMounted(async () => {
  await fetchOptions()
  await fetchProfiles()
})
</script>

<template>
  <div class="page-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>资质管理（能力范围配置）</span>
          <el-button type="primary" :icon="Plus" @click="openCreate">
            新增资质配置
          </el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="profileList" stripe border>
        <el-table-column prop="name" label="配置名称" min-width="220" show-overflow-tooltip />
        <el-table-column label="是否生效" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '生效中' : '未生效' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="允许数量" min-width="240">
          <template #default="{ row }">
            <div style="line-height: 1.6">
              <div>标准：{{ row.allowed_standards?.length ?? 0 }}</div>
              <div>方法：{{ row.allowed_test_methods?.length ?? 0 }}</div>
              <div>模板：{{ row.allowed_record_templates?.length ?? 0 }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增资质配置' : '编辑资质配置'" width="820px" destroy-on-close>
      <el-form label-width="120px">
        <el-form-item label="配置名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="是否生效">
          <el-switch v-model="form.is_active" />
        </el-form-item>
        <el-form-item label="有效期（可选）">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="起">
                <el-date-picker v-model="form.valid_from" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="止">
                <el-date-picker v-model="form.valid_to" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form-item>

        <el-divider>能力范围</el-divider>

        <el-form-item label="允许标准">
          <el-select
            v-model="form.allowed_standards"
            multiple
            filterable
            placeholder="选择标准"
            style="width: 100%"
            :loading="optionsLoading"
          >
            <el-option
              v-for="s in standards"
              :key="s.id"
              :label="`${s.standard_no} ${s.name}`"
              :value="s.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="允许检测方法">
          <el-select
            v-model="form.allowed_test_methods"
            multiple
            filterable
            placeholder="选择检测方法"
            style="width: 100%"
            :loading="optionsLoading"
          >
            <el-option
              v-for="m in methods"
              :key="m.id"
              :label="`${m.standard_no} ${m.name}`"
              :value="m.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="允许原始记录模板">
          <el-select
            v-model="form.allowed_record_templates"
            multiple
            filterable
            placeholder="选择原始记录模板"
            style="width: 100%"
            :loading="optionsLoading"
          >
            <el-option
              v-for="t in templates"
              :key="t.id"
              :label="`${t.name} (${t.code})`"
              :value="t.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">
          {{ dialogMode === 'create' ? '创建' : '保存' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

