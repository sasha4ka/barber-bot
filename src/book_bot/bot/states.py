from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    waiting_for_phone = State()


class MainMenuStates(StatesGroup):
    pass


class CreateAppointmentStates(StatesGroup):
    select_slot = State()
    comfirm = State()
