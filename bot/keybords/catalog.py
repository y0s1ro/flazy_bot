from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def build_category_keyboard(category_data, level=0, parent_id=None, part = 0):

    one_page = False
    builder = InlineKeyboardBuilder()
    selected_categories = category_data
    if len(category_data.keys()) > 9:
        selected_keys = sorted(category_data.keys(), key=lambda x: x.split('&', 1)[0])
        if (part+1)*9 > len(category_data.keys()):
            selected_keys = list(category_data.keys())[part*9:]
        else:
            selected_keys = list(category_data.keys())[part*9:(part+1)*9]
        selected_categories = {k: category_data[k] for k in selected_keys}
    else:
        one_page = True
    for key, item in sorted(selected_categories.items()):
        if key == "Status":
            continue

        if selected_categories[key]["Status"] == "False":
            continue
        # Extract the display name (removing the prefix like "1&")
        id, display_name = key.split('&*', 1) if '&*' in key else key.split('&', 1)
        
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
    builder.adjust(3)
    if part is not None and not one_page:
        builder.row(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"prev_{part}_{level}_{parent_id}" if parent_id else f"prev_{part}" if part>=len(category_data.keys())//9 else "no_action"
            ),
            InlineKeyboardButton(
                text=f"{part+1}/{len(category_data.keys())//9+1}",
                callback_data="no_action"
            ),
            InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=f"next_{part}_{level}_{parent_id}" if parent_id else f"next_{part}" if part == 0 else "no_action"
            )
        )
    if level > 0 and not parent_id:
        level = 0  # Reset level if no parent_id is provided
    if level > 0:
        # Add a back button if we are not at the top level
        prev_page = parent_id.rsplit("_", 1)[0]
        back_callback_data = f"c_{level-1}_{prev_page}" if (parent_id and "_" in parent_id) else f"c_{level-1}"
        builder.row(InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=back_callback_data
        ))
    return builder.as_markup()

async def build_product_keyboard(category_path_ids, is_auto_product=False, num_of_products=None):
    builder = InlineKeyboardBuilder()
    if is_auto_product:
        # If it's an auto product, we don't show the "Buy" button
        for i in range(num_of_products):
            builder.add(InlineKeyboardButton(
                text=f"{i+1} шт.",
                callback_data=f"b_{'_'.join(category_path_ids)}_{category_path_ids[-1]}_{i+1}a"
            ))
            if i==9:
                break
    if not is_auto_product:
        builder.add(InlineKeyboardButton(
            text="🛒 Купить",
            callback_data=f"b_{'_'.join(category_path_ids)}_{category_path_ids[-1]}"
        ))
    builder.adjust(5)
    # Add "Назад" button at the bottom, on a new row
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=f"c_{len(category_path_ids)-1}_{'_'.join(category_path_ids[:-1])}"
        )
    )
    return builder.as_markup()

async def build_region_keyboard(regions, callback_product):
    builder = InlineKeyboardBuilder()
    for i, region in enumerate(regions):
        builder.add(InlineKeyboardButton(
            text=region,
            callback_data=f"{callback_product}r{i}"
        ))
    builder.row(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data=f"p_{'_'.join(callback_product.split('_')[1:-1])}"
    ))
    return builder.as_markup()

async def build_review_keyboard(order_number = None):
    builder = InlineKeyboardBuilder()
    callback_data = f"reviewo_{order_number}" if order_number else "review"
    builder.add(InlineKeyboardButton(
        text="Оставить отзыв",
        callback_data=callback_data
    ))
    builder.row(InlineKeyboardButton(
        text="Отмена",
        callback_data="no_review"
    ))
    return builder.as_markup()

async def build_review_rating_keyboard():
    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.add(InlineKeyboardButton(
            text=f"{i} ⭐",
            callback_data=f"rev_rating_{i}"
        ))
    return builder.as_markup()