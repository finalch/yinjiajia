# SF快递API环境配置说明

## 环境变量配置

### 1. 环境选择
```bash
# 沙盒环境（默认）
export SF_ENV=sandbox

# 生产环境
export SF_ENV=production
```

### 2. 生产环境配置
```bash
# 生产环境必须设置以下环境变量
export SF_PARTNER_ID=your_production_partner_id
export SF_SECRET=your_production_secret
```

### 3. 完整配置示例

#### 沙盒环境
```bash
export SF_ENV=sandbox
# 使用默认配置，无需额外设置
```

#### 生产环境
```bash
export SF_ENV=production
export SF_PARTNER_ID=your_real_partner_id
export SF_SECRET=your_real_secret
```

## 配置文件方式

你也可以在Python代码中直接设置环境变量：

```python
import os

# 设置环境
os.environ['SF_ENV'] = 'production'
os.environ['SF_PARTNER_ID'] = 'your_partner_id'
os.environ['SF_SECRET'] = 'your_secret'

# 然后导入SF客户端
from services.sf_client import sf_client
```

## 注意事项

1. **沙盒环境**：使用测试账号，适合开发和测试
2. **生产环境**：使用正式账号，需要从SF快递获取真实的partner_id和secret
3. **安全性**：生产环境的secret应该妥善保管，不要提交到代码仓库
4. **环境隔离**：确保不同环境使用不同的配置，避免混淆
