from django.test import Client


class APIClient(Client):
    def post(
        self,
        path,
        data=None,
        content_type="application/json",
        follow=False,
        secure=False,
        *,
        headers=None,
        **extra,
    ):
        return super().post(
            path=path,
            data=data,
            content_type=content_type,
            follow=follow,
            secure=secure,
            headers=headers,
            **extra,
        )
