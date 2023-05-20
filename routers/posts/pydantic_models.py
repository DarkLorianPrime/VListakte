from libraries.utils.pydantic_base import CustomModel


class CreatePostModel(CustomModel):
    title: str
    text: str
    is_published: bool