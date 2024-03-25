class NotificationStatusEnum(str):
    unread = 'unread'
    read = 'read'

class StatusEnum(str):
    approved = 'approved'
    pending = 'pending'
    rejected = 'rejected'

class PermissionEnum(str):
    users = "users"
    roles = 'roles'
    permissions = 'permissions'
    permission_detail = 'permission_detail'
    schedules = 'schedules'
    statuses = 'statuses'
    users_meta = 'users_meta'
    user_meta_detail = 'user_meta_detail'
    rooms = 'rooms'
    room_detail = 'room_detail'
    categories = 'categories'
    menu = 'menu'
    sub_menu = 'sub_menu'
    subject_menu = 'subject_menu'
    customer_service = 'customer_service'


class PermissionDetailEnum(str):
    read = 'read'
    create = 'create'
    write = 'write'
    delete = 'delete'

class UserRoleEnum(str):
    admin = "admin"
    operators = "operators"
    commentators = "commentators"
    customer_service = "customer_service"