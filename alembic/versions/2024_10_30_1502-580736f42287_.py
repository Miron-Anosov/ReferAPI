"""empty message

Revision ID: 580736f42287
Revises: 
Create Date: 2024-10-30 15:02:21.093395

"""  # noqa W291 D400

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "580736f42287"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###  # noqa D103
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "auth",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_table(
        "refer",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("id_referrer", sa.UUID(), nullable=False),
        sa.Column("id_referred", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_referred"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["id_referrer"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_refer_id_referred"), "refer", ["id_referred"], unique=False
    )
    op.create_index(
        op.f("ix_refer_id_referrer"), "refer", ["id_referrer"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###  # noqa D103
    op.drop_index(op.f("ix_refer_id_referrer"), table_name="refer")
    op.drop_index(op.f("ix_refer_id_referred"), table_name="refer")
    op.drop_table("refer")
    op.drop_table("auth")
    op.drop_table("users")
    # ### end Alembic commands ###
