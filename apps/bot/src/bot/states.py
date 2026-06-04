from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_for_phone = State()


class MainMenuStates(StatesGroup):
    profile = State()


class CreateAppointmentStates(StatesGroup):
    select_master = State()
    select_slot = State()
    confirm = State()


class RescheduleAppointmentStates(StatesGroup):
    select_master = State()
    select_slot = State()
    confirm = State()


class AdminPanelStates(StatesGroup):
    main_menu = State()


class MasterCreationStates(StatesGroup):
    get_name = State()
    select_profile = State()
    waiting_for_password = State()
    confirm = State()
