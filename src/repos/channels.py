from sqlalchemy import delete, insert, select

from src.models.notifications import NotificationChannel
from src.schemas.notifications import NotificationChannelDTO
from src.repos.base import BaseRepository
from src.schemas.channels import UserChannelDTO
from src.models.users import UserContactChannel


class ChannelRepository(BaseRepository):
    model = UserContactChannel
    schema = UserChannelDTO

    async def get_all_filtered_by_ids(self, ids_list: list):
        query = (
            select(self.model.id)
            .select_from(self.model)
            .filter(
                self.model.id.in_(ids_list),
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class NotificationChannelRepository(BaseRepository):
    model = NotificationChannel
    schema = NotificationChannelDTO

    async def update_all(self, notification_id: int, channels_ids: list[int]):
        ids_to_delete = (
            select(self.model.id)
            .select_from(self.model)
            .filter(
                self.model.notification_id == notification_id,
                self.model.channel_id.notin_(channels_ids),
            )
        )

        delete_stmt = delete(self.model).filter(self.model.id.in_(ids_to_delete))
        await self.session.execute(delete_stmt)

        add_new_notification_channels = insert(self.model).from_select(
            ["notification_id", "channel_id"],
            select(notification_id, UserContactChannel.id).filter(
                UserContactChannel.id.in_(channels_ids),
                UserContactChannel.id.notin_(
                    select(self.model.additional_id)
                    .select_from(self.model)
                    .filter(self.model.notification_id == notification_id)
                ),
            ),
        )

        await self.session.execute(add_new_notification_channels)