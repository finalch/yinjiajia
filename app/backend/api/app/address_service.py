from models import db, Address
from typing import List, Optional, Dict, Any

class AddressService:
    """地址服务层 - 封装地址相关的业务逻辑"""
    
    @staticmethod
    def get_user_addresses(user_id: int) -> List[Dict[str, Any]]:
        """获取用户的所有地址"""
        addresses = Address.query.filter_by(user_id=user_id).order_by(
            Address.is_default.desc(), 
            Address.created_at.desc()
        ).all()
        
        address_list = []
        for addr in addresses:
            address_list.append({
                'id': addr.id,
                'receiver_name': addr.receiver_name,
                'phone': addr.phone,
                'province': addr.province,
                'city': addr.city,
                'district': addr.district,
                'detail_address': addr.detail_address,
                'is_default': addr.is_default,
                'full_address': f"{addr.province}{addr.city}{addr.district}{addr.detail_address}"
            })
        
        return address_list
    
    @staticmethod
    def get_default_address(user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户的默认地址"""
        default_address = Address.query.filter_by(
            user_id=user_id, 
            is_default=True
        ).first()
        
        if not default_address:
            return None
            
        return {
            'id': default_address.id,
            'receiver_name': default_address.receiver_name,
            'phone': default_address.phone,
            'province': default_address.province,
            'city': default_address.city,
            'district': default_address.district,
            'detail_address': default_address.detail_address,
            'is_default': default_address.is_default,
            'full_address': f"{default_address.province}{default_address.city}{default_address.district}{default_address.detail_address}"
        }
    
    @staticmethod
    def get_address_by_id(address_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取地址"""
        address = Address.query.filter_by(id=address_id, user_id=user_id).first()
        
        if not address:
            return None
            
        return {
            'id': address.id,
            'receiver_name': address.receiver_name,
            'phone': address.phone,
            'province': address.province,
            'city': address.city,
            'district': address.district,
            'detail_address': address.detail_address,
            'is_default': address.is_default,
            'full_address': f"{address.province}{address.city}{address.district}{address.detail_address}"
        }
    
    @staticmethod
    def create_address(user_id: int, address_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新地址"""
        # 如果设置为默认地址，先取消其他默认地址
        if address_data.get('is_default'):
            Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
        
        new_address = Address(
            user_id=user_id,
            receiver_name=address_data['receiver_name'],
            phone=address_data['phone'],
            province=address_data['province'],
            city=address_data['city'],
            district=address_data['district'],
            detail_address=address_data['detail_address'],
            is_default=address_data.get('is_default', False)
        )
        
        db.session.add(new_address)
        db.session.commit()
        
        return {
            'id': new_address.id,
            'receiver_name': new_address.receiver_name,
            'phone': new_address.phone,
            'province': new_address.province,
            'city': new_address.city,
            'district': new_address.district,
            'detail_address': new_address.detail_address,
            'is_default': new_address.is_default,
            'full_address': f"{new_address.province}{new_address.city}{new_address.district}{new_address.detail_address}"
        }
    
    @staticmethod
    def update_address(address_id: int, user_id: int, address_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新地址"""
        address = Address.query.filter_by(id=address_id, user_id=user_id).first()
        
        if not address:
            return None
        
        # 如果设置为默认地址，先取消其他默认地址
        if address_data.get('is_default'):
            Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
        
        # 更新地址信息
        for key, value in address_data.items():
            if hasattr(address, key):
                setattr(address, key, value)
        
        db.session.commit()
        
        return {
            'id': address.id,
            'receiver_name': address.receiver_name,
            'phone': address.phone,
            'province': address.province,
            'city': address.city,
            'district': address.district,
            'detail_address': address.detail_address,
            'is_default': address.is_default,
            'full_address': f"{address.province}{address.city}{address.district}{address.detail_address}"
        }
    
    @staticmethod
    def delete_address(address_id: int, user_id: int) -> bool:
        """删除地址"""
        address = Address.query.filter_by(id=address_id, user_id=user_id).first()
        
        if not address:
            return False
        
        db.session.delete(address)
        db.session.commit()
        
        return True
    
    @staticmethod
    def set_default_address(address_id: int, user_id: int) -> bool:
        """设置默认地址"""
        # 先取消所有默认地址
        Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
        
        # 设置新的默认地址
        address = Address.query.filter_by(id=address_id, user_id=user_id).first()
        if not address:
            return False
        
        address.is_default = True
        db.session.commit()
        
        return True 