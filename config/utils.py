# プロジェクト全体で使用する共通処理などをまとめる


def get_resized_image_url(
    image_url, width=None, height=None, crop="fill", gravity="auto"
):
    """
    Cloudinaryの画像URLをリサイズ用URLに変換する処理

    Args:
        image_url (str): 元の画像URL
        width (int): リサイズ後の幅（オプショナル）
        height (int): リサイズ後の高さ（オプショナル）
        crop (str): クロップ方法（デフォルトは"fill")
        gravity (str): クロップ位置（デフォルトは"auto"）

    Returns:
        str: リサイズ後の画像URL
    """
    if not image_url:
        return None

    # URLを分割してリサイズ用のトランスフォーメーションを挿入
    parts = image_url.split("/image/upload/")
    if len(parts) != 2:
        # URLの形式が期待と異なる場合、元のURLを返す
        return image_url

    # 動的なリサイズ設定（引数のパラメータを含める）
    transformation_list = [f"c_{crop}", f"g_{gravity}"]
    if width is not None:
        transformation_list.append(f"w_{width}")
    if height is not None:
        transformation_list.append(f"h_{height}")

    # リサイズ設定用の文字列作成
    transformation_str = ",".join(transformation_list)

    # リサイズ後のURL整形
    resized_url = f"{parts[0]}/image/upload/{transformation_str}/{parts[1]}"
    return resized_url
