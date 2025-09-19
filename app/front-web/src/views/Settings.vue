<template>
  <div class="settings">
    <div class="page-header">
      <h1>系统设置</h1>
    </div>

    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- 基本设置 -->
      <el-tab-pane label="基本设置" name="basic">
        <el-card>
          <el-form :model="basicForm" :rules="basicRules" ref="basicFormRef" label-width="120px">
            <el-form-item label="店铺名称" prop="shopName">
              <el-input v-model="basicForm.shopName" placeholder="请输入店铺名称" />
            </el-form-item>
            <el-form-item label="店铺简介" prop="shopDescription">
              <el-input
                v-model="basicForm.shopDescription"
                type="textarea"
                :rows="3"
                placeholder="请输入店铺简介"
              />
            </el-form-item>
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="basicForm.phone" placeholder="请输入联系电话" />
            </el-form-item>
            <el-form-item label="联系邮箱" prop="email">
              <el-input v-model="basicForm.email" placeholder="请输入联系邮箱" />
            </el-form-item>
            <el-form-item label="店铺地址" prop="detail_address">
              <el-input v-model="basicForm.detail_address" placeholder="请输入店铺地址" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveBasicSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 安全设置 -->
      <el-tab-pane label="安全设置" name="security">
        <el-card>
          <el-form :model="securityForm" :rules="securityRules" ref="securityFormRef" label-width="120px">
            <el-form-item label="当前密码" prop="currentPassword">
              <el-input 
                v-model="securityForm.currentPassword" 
                type="password" 
                placeholder="请输入当前密码"
                show-password
              />
            </el-form-item>
            <el-form-item label="新密码" prop="newPassword">
              <el-input 
                v-model="securityForm.newPassword" 
                type="password" 
                placeholder="请输入新密码"
                show-password
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input 
                v-model="securityForm.confirmPassword" 
                type="password" 
                placeholder="请再次输入新密码"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="changePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 通知设置 -->
      <el-tab-pane label="通知设置" name="notification">
        <el-card>
          <el-form :model="notificationForm" label-width="120px">
            <el-form-item label="订单通知">
              <el-switch v-model="notificationForm.orderNotification" />
              <span class="form-tip">新订单时发送通知</span>
            </el-form-item>
            <el-form-item label="库存预警">
              <el-switch v-model="notificationForm.stockWarning" />
              <span class="form-tip">库存不足时发送通知</span>
            </el-form-item>
            <el-form-item label="评价通知">
              <el-switch v-model="notificationForm.reviewNotification" />
              <span class="form-tip">收到新评价时发送通知</span>
            </el-form-item>
            <el-form-item label="系统通知">
              <el-switch v-model="notificationForm.systemNotification" />
              <span class="form-tip">系统维护等重要通知</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveNotificationSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 仓库管理 -->
      <el-tab-pane label="仓库管理" name="warehouse">
        <el-card>
          <div class="warehouse-header">
            <h3>仓库信息管理</h3>
            <el-button type="primary" @click="addWarehouse">新增仓库</el-button>
          </div>
          
          <el-table :data="warehouseList" style="width: 100%" v-loading="warehouseLoading">
            <el-table-column prop="name" label="仓库名称" width="150" />
            <el-table-column label="仓库地址" width="300">
              <template #default="scope">
                <div class="address-display">
                  <div v-if="scope.row.province || scope.row.city || scope.row.district || scope.row.detail_address" class="address-content">
                    <!-- 省市区信息 -->
                    <div v-if="scope.row.province || scope.row.city || scope.row.district" class="region-line">
                      <span v-if="scope.row.province" class="region-item province">{{ scope.row.province }}</span>
                      <span v-if="scope.row.city" class="region-item city">{{ scope.row.city }}</span>
                      <span v-if="scope.row.district" class="region-item district">{{ scope.row.district }}</span>
                    </div>
                    <!-- 详细地址 -->
                    <div v-if="scope.row.detail_address" class="detail-line">
                      {{ scope.row.detail_address }}
                    </div>
                  </div>
                  <div v-else class="no-address">
                    <el-icon><LocationInformation /></el-icon>
                    <span>未设置地址</span>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="contact_person" label="联系人" width="120" />
            <el-table-column prop="contact_phone" label="联系电话" width="130" />
            <el-table-column prop="created_at" label="创建时间" width="160" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" @click="editWarehouse(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteWarehouse(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 关于我们 -->
      <el-tab-pane label="关于我们" name="about">
        <el-card>
          <div class="about-content">
            <div class="app-info">
              <h3>银家家商家后台管理系统</h3>
              <p>版本：v1.0.0</p>
              <p>更新时间：2024年1月15日</p>
            </div>
            <div class="contact-info">
              <h4>联系我们</h4>
              <p>客服电话：400-123-4567</p>
              <p>客服邮箱：support@yinjiajia.com</p>
              <p>官方网站：www.yinjiajia.com</p>
            </div>
            <div class="copyright">
              <p>© 2024 银家家科技有限公司 版权所有</p>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 仓库管理对话框 -->
    <el-dialog 
      v-model="warehouseDialogVisible" 
      :title="warehouseDialogTitle" 
      width="600px"
      @close="resetWarehouseForm"
    >
      <el-form :model="warehouseForm" :rules="warehouseRules" ref="warehouseFormRef" label-width="100px">
        <el-form-item label="仓库名称" prop="name">
          <el-input v-model="warehouseForm.name" placeholder="请输入仓库名称" />
        </el-form-item>
        <el-form-item label="所在省份" prop="province">
          <el-select 
            v-model="warehouseForm.province" 
            placeholder="请选择省份"
            style="width: 100%"
            @change="handleProvinceChange"
            clearable
          >
            <el-option 
              v-for="province in provinces" 
              :key="province.code"
              :label="province.name"
              :value="province.name"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="所在城市" prop="city">
          <el-select 
            v-model="warehouseForm.city" 
            placeholder="请选择城市"
            style="width: 100%"
            @change="handleCityChange"
            :disabled="!warehouseForm.province"
            clearable
          >
            <el-option 
              v-for="city in cities" 
              :key="city.code"
              :label="city.name"
              :value="city.name"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="所在区县" prop="district">
          <el-select 
            v-model="warehouseForm.district" 
            placeholder="请选择区县"
            style="width: 100%"
            :disabled="!warehouseForm.city"
            clearable
          >
            <el-option 
              v-for="district in districts" 
              :key="district.code"
              :label="district.name"
              :value="district.name"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="详细地址" prop="detail_address">
          <el-input 
            v-model="warehouseForm.detail_address" 
            type="textarea" 
            :rows="2"
            placeholder="请输入详细地址（街道、门牌号等）"
          />
        </el-form-item>
        <el-form-item label="联系人" prop="contact_person">
          <el-input v-model="warehouseForm.contact_person" placeholder="请输入联系人姓名" />
        </el-form-item>
        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="warehouseForm.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input 
            v-model="warehouseForm.remark" 
            type="textarea" 
            :rows="2"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="warehouseDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveWarehouse">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { LocationInformation } from '@element-plus/icons-vue'
import warehouseService from '../services/warehouseService'

export default {
  name: 'Settings',
  setup() {
    // 从localStorage获取保存的tab状态，默认为'basic'
    const activeTab = ref(localStorage.getItem('settings_active_tab') || 'basic')
    const basicFormRef = ref()
    const securityFormRef = ref()
    const warehouseFormRef = ref()
    
    // 仓库管理相关状态
    const warehouseDialogVisible = ref(false)
    const warehouseDialogTitle = ref('新增仓库')
    const warehouseLoading = ref(false)
    const isEditMode = ref(false)
    const currentWarehouseId = ref(null)
    
    // 基本设置表单
    const basicForm = reactive({
      shopName: '银家家数码专营店',
      shopDescription: '专业销售各类数码产品，品质保证，服务至上。',
      phone: '400-123-4567',
      email: 'contact@yinjiajia.com',
      detail_address: '北京市朝阳区xxx街道xxx号'
    })
    
    const basicRules = {
      shopName: [
        { required: true, message: '请输入店铺名称', trigger: 'blur' }
      ],
      phone: [
        { required: true, message: '请输入联系电话', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入联系邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ]
    }
    
    // 安全设置表单
    const securityForm = reactive({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    const securityRules = {
      currentPassword: [
        { required: true, message: '请输入当前密码', trigger: 'blur' }
      ],
      newPassword: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请确认新密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== securityForm.newPassword) {
              callback(new Error('两次输入的密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }
    
    // 通知设置表单
    const notificationForm = reactive({
      orderNotification: true,
      stockWarning: true,
      reviewNotification: true,
      systemNotification: true
    })
    
    // 仓库管理表单
    const warehouseForm = reactive({
      name: '',
      province: '',
      city: '',
      district: '',
      detail_address: '',
      contact_person: '',
      contact_phone: '',
      remark: ''
    })
    
    const warehouseRules = {
      name: [
        { required: true, message: '请输入仓库名称', trigger: 'blur' }
      ],
      province: [
        { required: true, message: '请选择省份', trigger: 'change' }
      ],
      city: [
        { required: true, message: '请选择城市', trigger: 'change' }
      ],
      district: [
        { required: true, message: '请选择区县', trigger: 'change' }
      ],
      detail_address: [
        { required: true, message: '请输入详细地址', trigger: 'blur' }
      ],
      contact_person: [
        { required: true, message: '请输入联系人', trigger: 'blur' }
      ],
      contact_phone: [
        { required: true, message: '请输入联系电话', trigger: 'blur' },
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
      ]
    }
    
    // 仓库列表数据
    const warehouseList = ref([])
    
    // 省市区数据
    const provinces = ref([])
    const cities = ref([])
    const districts = ref([])
    
    // 省市区数据（简化版，实际项目中可以从API获取）
    const regionData = {
      '110000': { name: '北京市', children: {
        '110100': { name: '北京市', children: {
          '110101': { name: '东城区' },
          '110102': { name: '西城区' },
          '110105': { name: '朝阳区' },
          '110106': { name: '丰台区' },
          '110107': { name: '石景山区' },
          '110108': { name: '海淀区' },
          '110109': { name: '门头沟区' },
          '110111': { name: '房山区' },
          '110112': { name: '通州区' },
          '110113': { name: '顺义区' },
          '110114': { name: '昌平区' },
          '110115': { name: '大兴区' },
          '110116': { name: '怀柔区' },
          '110117': { name: '平谷区' },
          '110118': { name: '密云区' },
          '110119': { name: '延庆区' }
        }}
      }},
      '120000': { name: '天津市', children: {
        '120100': { name: '天津市', children: {
          '120101': { name: '和平区' },
          '120102': { name: '河东区' },
          '120103': { name: '河西区' },
          '120104': { name: '南开区' },
          '120105': { name: '河北区' },
          '120106': { name: '红桥区' },
          '120110': { name: '东丽区' },
          '120111': { name: '西青区' },
          '120112': { name: '津南区' },
          '120113': { name: '北辰区' },
          '120114': { name: '武清区' },
          '120115': { name: '宝坻区' },
          '120116': { name: '滨海新区' },
          '120117': { name: '宁河区' },
          '120118': { name: '静海区' },
          '120119': { name: '蓟州区' }
        }}
      }},
      '130000': { name: '河北省', children: {
        '130100': { name: '石家庄市', children: {
          '130102': { name: '长安区' },
          '130104': { name: '桥西区' },
          '130105': { name: '新华区' },
          '130107': { name: '井陉矿区' },
          '130108': { name: '裕华区' },
          '130109': { name: '藁城区' },
          '130110': { name: '鹿泉区' },
          '130111': { name: '栾城区' },
          '130121': { name: '井陉县' },
          '130123': { name: '正定县' },
          '130125': { name: '行唐县' },
          '130126': { name: '灵寿县' },
          '130127': { name: '高邑县' },
          '130128': { name: '深泽县' },
          '130129': { name: '赞皇县' },
          '130130': { name: '无极县' },
          '130131': { name: '平山县' },
          '130132': { name: '元氏县' },
          '130133': { name: '赵县' },
          '130183': { name: '晋州市' },
          '130184': { name: '新乐市' }
        }},
        '130200': { name: '唐山市', children: {
          '130202': { name: '路南区' },
          '130203': { name: '路北区' },
          '130204': { name: '古冶区' },
          '130205': { name: '开平区' },
          '130207': { name: '丰南区' },
          '130208': { name: '丰润区' },
          '130209': { name: '曹妃甸区' },
          '130223': { name: '滦县' },
          '130224': { name: '滦南县' },
          '130225': { name: '乐亭县' },
          '130227': { name: '迁西县' },
          '130229': { name: '玉田县' },
          '130281': { name: '遵化市' },
          '130283': { name: '迁安市' }
        }}
      }},
      '310000': { name: '上海市', children: {
        '310100': { name: '上海市', children: {
          '310101': { name: '黄浦区' },
          '310104': { name: '徐汇区' },
          '310105': { name: '长宁区' },
          '310106': { name: '静安区' },
          '310107': { name: '普陀区' },
          '310109': { name: '虹口区' },
          '310110': { name: '杨浦区' },
          '310112': { name: '闵行区' },
          '310113': { name: '宝山区' },
          '310114': { name: '嘉定区' },
          '310115': { name: '浦东新区' },
          '310116': { name: '金山区' },
          '310117': { name: '松江区' },
          '310118': { name: '青浦区' },
          '310120': { name: '奉贤区' },
          '310151': { name: '崇明区' }
        }}
      }},
      '320000': { name: '江苏省', children: {
        '320100': { name: '南京市', children: {
          '320102': { name: '玄武区' },
          '320104': { name: '秦淮区' },
          '320105': { name: '建邺区' },
          '320106': { name: '鼓楼区' },
          '320111': { name: '浦口区' },
          '320113': { name: '栖霞区' },
          '320114': { name: '雨花台区' },
          '320115': { name: '江宁区' },
          '320116': { name: '六合区' },
          '320117': { name: '溧水区' },
          '320118': { name: '高淳区' }
        }},
        '320200': { name: '无锡市', children: {
          '320205': { name: '锡山区' },
          '320206': { name: '惠山区' },
          '320211': { name: '滨湖区' },
          '320213': { name: '梁溪区' },
          '320214': { name: '新吴区' },
          '320281': { name: '江阴市' },
          '320282': { name: '宜兴市' }
        }}
      }},
      '330000': { name: '浙江省', children: {
        '330100': { name: '杭州市', children: {
          '330102': { name: '上城区' },
          '330105': { name: '拱墅区' },
          '330106': { name: '西湖区' },
          '330108': { name: '滨江区' },
          '330109': { name: '萧山区' },
          '330110': { name: '余杭区' },
          '330111': { name: '富阳区' },
          '330112': { name: '临安区' },
          '330113': { name: '临平区' },
          '330114': { name: '钱塘区' },
          '330122': { name: '桐庐县' },
          '330127': { name: '淳安县' },
          '330182': { name: '建德市' }
        }}
      }},
      '440000': { name: '广东省', children: {
        '440100': { name: '广州市', children: {
          '440103': { name: '荔湾区' },
          '440104': { name: '越秀区' },
          '440105': { name: '海珠区' },
          '440106': { name: '天河区' },
          '440111': { name: '白云区' },
          '440112': { name: '黄埔区' },
          '440113': { name: '番禺区' },
          '440114': { name: '花都区' },
          '440115': { name: '南沙区' },
          '440117': { name: '从化区' },
          '440118': { name: '增城区' }
        }},
        '440300': { name: '深圳市', children: {
          '440303': { name: '罗湖区' },
          '440304': { name: '福田区' },
          '440305': { name: '南山区' },
          '440306': { name: '宝安区' },
          '440307': { name: '龙岗区' },
          '440308': { name: '盐田区' },
          '440309': { name: '龙华区' },
          '440310': { name: '坪山区' },
          '440311': { name: '光明区' }
        }}
      }}
    }
    
    // 方法
    const saveBasicSettings = async () => {
      try {
        await basicFormRef.value.validate()
        ElMessage.success('基本设置保存成功')
      } catch (error) {
        ElMessage.error('请完善基本信息')
      }
    }
    
    const changePassword = async () => {
      try {
        await securityFormRef.value.validate()
        ElMessage.success('密码修改成功')
        // 清空表单
        securityForm.currentPassword = ''
        securityForm.newPassword = ''
        securityForm.confirmPassword = ''
      } catch (error) {
        ElMessage.error('请完善密码信息')
      }
    }
    
    const saveNotificationSettings = () => {
      ElMessage.success('通知设置保存成功')
    }
    
    // 仓库管理方法
    const addWarehouse = () => {
      isEditMode.value = false
      warehouseDialogTitle.value = '新增仓库'
      warehouseDialogVisible.value = true
      resetWarehouseForm()
    }
    
    const editWarehouse = async (warehouse) => {
      isEditMode.value = true
      warehouseDialogTitle.value = '编辑仓库'
      currentWarehouseId.value = warehouse.id
      
      // 填充表单数据
      warehouseForm.name = warehouse.name
      warehouseForm.contact_person = warehouse.contact_person
      warehouseForm.contact_phone = warehouse.contact_phone
      warehouseForm.remark = warehouse.remark
      
      // 解析地址信息（warehouse中的省市区已经是名称）
      if (warehouse.province) {
        warehouseForm.province = warehouse.province
        // 先设置省份，然后加载对应的城市列表
        handleProvinceChange(warehouse.province)
        
        // 等待城市数据加载完成
        await nextTick()
        
        if (warehouse.city) {
          warehouseForm.city = warehouse.city
          // 先设置城市，然后加载对应的区县列表
          handleCityChange(warehouse.city)
          
          // 等待区县数据加载完成
          await nextTick()
          
          if (warehouse.district) {
            warehouseForm.district = warehouse.district
          }
        }
      }
      
      warehouseForm.detail_address = warehouse.detail_address || ''
      
      warehouseDialogVisible.value = true
    }
    
    const saveWarehouse = async () => {
      try {
        await warehouseFormRef.value.validate()
        
        // 准备提交数据，确保使用省市区名称而不是code
        const submitData = {
          name: warehouseForm.name,
          province: warehouseForm.province, // 这里已经是名称
          city: warehouseForm.city, // 这里已经是名称
          district: warehouseForm.district, // 这里已经是名称
          detail_address: warehouseForm.detail_address,
          contact_person: warehouseForm.contact_person,
          contact_phone: warehouseForm.contact_phone,
          remark: warehouseForm.remark
        }
        
        if (isEditMode.value) {
          // 编辑模式
          const result = await warehouseService.updateWarehouse(currentWarehouseId.value, submitData)
          if (result.success) {
            ElMessage.success(result.message || '仓库信息更新成功')
            await loadWarehouseList() // 重新加载列表
          } else {
            ElMessage.error(result.message || '仓库信息更新失败')
          }
        } else {
          // 新增模式
          const result = await warehouseService.createWarehouse(submitData)
          if (result.success) {
            ElMessage.success(result.message || '仓库添加成功')
            await loadWarehouseList() // 重新加载列表
          } else {
            ElMessage.error(result.message || '仓库添加失败')
          }
        }
        
        warehouseDialogVisible.value = false
        resetWarehouseForm()
      } catch (error) {
        ElMessage.error('请完善仓库信息')
      }
    }
    
    
    const deleteWarehouse = async (warehouse) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除仓库"${warehouse.name}"吗？删除后不可恢复！`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        const result = await warehouseService.deleteWarehouse(warehouse.id)
        if (result.success) {
          ElMessage.success(result.message || '仓库删除成功')
          await loadWarehouseList() // 重新加载列表
        } else {
          ElMessage.error(result.message || '仓库删除失败')
        }
      } catch (error) {
        // 用户取消操作
      }
    }
    
    const resetWarehouseForm = () => {
      warehouseForm.name = ''
      warehouseForm.province = ''
      warehouseForm.city = ''
      warehouseForm.district = ''
      warehouseForm.detail_address = ''
      warehouseForm.contact_person = ''
      warehouseForm.contact_phone = ''
      warehouseForm.remark = ''
      currentWarehouseId.value = null
      isEditMode.value = false
      
      // 清空省市区选择
      cities.value = []
      districts.value = []
    }
    
    // 加载仓库列表
    const loadWarehouseList = async () => {
      warehouseLoading.value = true
      try {
        const result = await warehouseService.getWarehouseList()
        if (result.success) {
          warehouseList.value = result.data
        } else {
          ElMessage.error(result.message || '加载仓库列表失败')
        }
      } catch (error) {
        console.error('加载仓库列表失败:', error)
        ElMessage.error('加载仓库列表失败')
      } finally {
        warehouseLoading.value = false
      }
    }
    
    // 省市区处理方法
    const initProvinces = () => {
      provinces.value = Object.keys(regionData).map(code => ({
        code,
        name: regionData[code].name
      }))
    }
    
    const handleProvinceChange = (provinceName) => {
      warehouseForm.city = ''
      warehouseForm.district = ''
      cities.value = []
      districts.value = []
      
      // 根据省份名称找到对应的code
      const provinceCode = provinces.value.find(p => p.name === provinceName)?.code
      if (provinceCode && regionData[provinceCode]) {
        cities.value = Object.keys(regionData[provinceCode].children || {}).map(code => ({
          code,
          name: regionData[provinceCode].children[code].name
        }))
      }
    }
    
    const handleCityChange = (cityName) => {
      warehouseForm.district = ''
      districts.value = []
      
      // 根据省份名称找到对应的code
      const provinceCode = provinces.value.find(p => p.name === warehouseForm.province)?.code
      if (cityName && provinceCode && regionData[provinceCode]) {
        // 在城市列表中查找对应的code
        const cityCode = cities.value.find(c => c.name === cityName)?.code
        if (cityCode) {
          const cityData = regionData[provinceCode].children[cityCode]
          if (cityData && cityData.children) {
            districts.value = Object.keys(cityData.children).map(code => ({
              code,
              name: cityData.children[code].name
            }))
          }
        }
      }
    }
    
    // 获取完整地址字符串
    const getFullAddress = (province, city, district, detail) => {
      const provinceName = provinces.value.find(p => p.code === province)?.name || ''
      const cityName = cities.value.find(c => c.code === city)?.name || ''
      const districtName = districts.value.find(d => d.code === district)?.name || ''
      
      return [provinceName, cityName, districtName, detail].filter(Boolean).join('')
    }
    
    // 解析地址字符串为省市区
    const parseAddress = (detail_address) => {
      // 这里可以根据实际需要实现地址解析逻辑
      // 暂时返回空值，需要根据实际数据结构调整
      return {
        province: '',
        city: '',
        district: '',
        detail_address: detail_address || ''
      }
    }
    
    // 监听tab变化，保存到localStorage
    watch(activeTab, (newTab) => {
      localStorage.setItem('settings_active_tab', newTab)
    })
    
    // 组件挂载时加载仓库列表和初始化省份
    onMounted(() => {
      loadWarehouseList()
      initProvinces()
    })
    
    return {
      activeTab,
      basicFormRef,
      securityFormRef,
      warehouseFormRef,
      basicForm,
      basicRules,
      securityForm,
      securityRules,
      notificationForm,
      warehouseForm,
      warehouseRules,
      warehouseList,
      warehouseDialogVisible,
      warehouseDialogTitle,
      warehouseLoading,
      provinces,
      cities,
      districts,
      saveBasicSettings,
      changePassword,
      saveNotificationSettings,
      addWarehouse,
      editWarehouse,
      saveWarehouse,
      deleteWarehouse,
      resetWarehouseForm,
      loadWarehouseList,
      handleProvinceChange,
      handleCityChange,
      getFullAddress
    }
  }
}
</script>

<style scoped>
.settings {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 100px);
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: clamp(1.5rem, 4vw, 2.5rem);
  color: #333;
  margin: 0;
  font-weight: 600;
}

.settings-tabs {
  margin-bottom: 32px;
}

.settings-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.settings-tabs :deep(.el-tabs__nav-wrap) {
  padding: 0 20px;
}

.settings-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  padding: 0 20px;
  height: 48px;
  line-height: 48px;
}

.settings-tabs :deep(.el-tabs__content) {
  padding: 0 20px;
}

.settings-tabs :deep(.el-card) {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: none;
}

.settings-tabs :deep(.el-card__body) {
  padding: 24px;
}

.form-tip {
  margin-left: 12px;
  color: #666;
  font-size: 0.9rem;
}

.about-content {
  padding: 24px 0;
}

.app-info {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
}

.app-info h3 {
  color: #333;
  margin-bottom: 12px;
  font-size: 1.4rem;
  font-weight: 600;
}

.app-info p {
  color: #666;
  margin-bottom: 8px;
  font-size: 1rem;
  line-height: 1.6;
}

.contact-info {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
}

.contact-info h4 {
  color: #333;
  margin-bottom: 12px;
  font-size: 1.2rem;
  font-weight: 600;
}

.contact-info p {
  color: #666;
  margin-bottom: 8px;
  font-size: 1rem;
  line-height: 1.6;
}

.copyright {
  text-align: center;
  color: #999;
  font-size: 0.9rem;
  margin-top: 24px;
}

.warehouse-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
  flex-wrap: wrap;
  gap: 16px;
}

.warehouse-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.3rem;
  font-weight: 600;
}

.warehouse-header .el-button {
  flex-shrink: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

/* 表格响应式 */
:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th) {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
}

:deep(.el-table td) {
  padding: 12px 0;
}

:deep(.el-table .cell) {
  padding: 0 12px;
}

/* 表单样式优化 */
:deep(.el-form-item__label) {
  font-weight: 500;
  color: #333;
}

:deep(.el-input__inner) {
  border-radius: 6px;
}

:deep(.el-textarea__inner) {
  border-radius: 6px;
}

:deep(.el-button) {
  border-radius: 6px;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .settings {
    max-width: 100%;
    padding: 16px;
  }
  
  .settings-tabs :deep(.el-tabs__content) {
    padding: 0 16px;
  }
  
  .settings-tabs :deep(.el-card__body) {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .settings {
    padding: 12px;
    min-height: calc(100vh - 80px);
  }
  
  .page-header {
    margin-bottom: 20px;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .settings-tabs {
    margin-bottom: 24px;
  }
  
  .settings-tabs :deep(.el-tabs__nav-wrap) {
    padding: 0 12px;
  }
  
  .settings-tabs :deep(.el-tabs__item) {
    font-size: 14px;
    padding: 0 16px;
    height: 44px;
    line-height: 44px;
  }
  
  .settings-tabs :deep(.el-tabs__content) {
    padding: 0 12px;
  }
  
  .settings-tabs :deep(.el-card__body) {
    padding: 16px;
  }
  
  .warehouse-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .warehouse-header h3 {
    font-size: 1.2rem;
  }
  
  /* 表格在小屏幕上的优化 */
  :deep(.el-table) {
    font-size: 14px;
  }
  
  :deep(.el-table th),
  :deep(.el-table td) {
    padding: 8px 0;
  }
  
  :deep(.el-table .cell) {
    padding: 0 8px;
  }
  
  /* 按钮组优化 */
  :deep(.el-table .el-button) {
    padding: 4px 8px;
    font-size: 12px;
  }
  
  /* 对话框优化 */
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }
  
  :deep(.el-dialog__body) {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .settings {
    padding: 8px;
  }
  
  .page-header h1 {
    font-size: 1.5rem;
  }
  
  .settings-tabs :deep(.el-tabs__nav-wrap) {
    padding: 0 8px;
  }
  
  .settings-tabs :deep(.el-tabs__item) {
    font-size: 13px;
    padding: 0 12px;
    height: 40px;
    line-height: 40px;
  }
  
  .settings-tabs :deep(.el-tabs__content) {
    padding: 0 8px;
  }
  
  .settings-tabs :deep(.el-card__body) {
    padding: 12px;
  }
  
  /* 表格进一步优化 */
  :deep(.el-table) {
    font-size: 12px;
  }
  
  :deep(.el-table th),
  :deep(.el-table td) {
    padding: 6px 0;
  }
  
  :deep(.el-table .cell) {
    padding: 0 6px;
  }
  
  /* 按钮进一步优化 */
  :deep(.el-table .el-button) {
    padding: 3px 6px;
    font-size: 11px;
  }
  
  /* 对话框进一步优化 */
  :deep(.el-dialog) {
    width: 98% !important;
  }
  
  :deep(.el-dialog__body) {
    padding: 16px;
  }
  
  .dialog-footer {
    margin-top: 20px;
    gap: 8px;
  }
  
  .dialog-footer .el-button {
    padding: 8px 16px;
    font-size: 14px;
  }
}

/* 横屏优化 */
@media (orientation: landscape) and (max-height: 600px) {
  .settings {
    min-height: calc(100vh - 60px);
  }
  
  .page-header {
    margin-bottom: 16px;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .settings-tabs {
    margin-bottom: 20px;
  }
  
  .settings-tabs :deep(.el-tabs__item) {
    height: 40px;
    line-height: 40px;
  }
}

/* 地址显示样式 */
.address-display {
  font-size: 14px;
  line-height: 1.5;
}

.address-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.region-line {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.region-item {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.region-item.province {
  background-color: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.region-item.city {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.region-item.district {
  background-color: #fff7e6;
  color: #fa8c16;
  border: 1px solid #ffd591;
}

.detail-line {
  color: #666;
  font-size: 13px;
  line-height: 1.4;
  word-break: break-all;
  padding: 4px 0;
  border-top: 1px solid #f0f0f0;
  margin-top: 2px;
}

.no-address {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #999;
  font-style: italic;
  font-size: 13px;
  padding: 8px 0;
}

.no-address .el-icon {
  font-size: 16px;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .address-display {
    font-size: 13px;
  }
  
  .region-item {
    font-size: 11px;
    padding: 1px 4px;
  }
  
  .detail-line {
    font-size: 12px;
  }
  
  .no-address {
    font-size: 12px;
  }
}
</style> 