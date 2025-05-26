from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def build_category_keyboard(category_data, level=0, parent_id=None):

    builder = InlineKeyboardBuilder()
    for key, item in sorted(category_data.items()):
        if key == "Status":
            continue

        if category_data[key]["Status"] == "False":
            continue
        # Extract the display name (removing the prefix like "1&")
        id, display_name = key.split('&', 1) if '&' in key else key
        
        if isinstance(item, dict) and "description" not in item:
            # This is a category or subcategory
            callback_data = f"c_{level}_{parent_id}_{id}" if parent_id else f"c_{level}_{id}"
            builder.add(InlineKeyboardButton(
                text=display_name,
                callback_data=callback_data
            ))
        elif isinstance(item, dict) and "description" in item:
            # This is a product
            callback_data = f"p_{parent_id}_{id}" if parent_id else f"p_{id}"
            builder.add(InlineKeyboardButton(
                text=display_name,
                callback_data=callback_data
            ))

    if level > 0 and not parent_id:
        level = 0  # Reset level if no parent_id is provided
    if level > 0:
        # Add a back button if we are not at the top level
        prev_page = parent_id.rsplit("_", 1)[0]
        back_callback_data = f"c_{level-1}_{prev_page}" if (parent_id and "_" in parent_id) else f"c_{level-1}"
        builder.add(InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=back_callback_data
        ))
    builder.adjust(3)
    return builder.as_markup()

async def build_product_keyboard(category_path_ids):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="🛒 Купить",
        callback_data=f"b_{'_'.join(category_path_ids)}_{category_path_ids[-1]}"
    ))
    builder.add(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data=f"c_{len(category_path_ids)-1}_{'_'.join(category_path_ids[:-1])}"
    ))
    return builder.as_markup()