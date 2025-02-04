"""credits_auctions_marathon_rules

Revision ID: 2e630d773e10
Revises: 91dcb1834daa
Create Date: 2024-12-21 03:08:09.073521

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2e630d773e10"
down_revision: Union[str, None] = "91dcb1834daa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "auctions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("comment", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("picture", sa.String(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=True),
        sa.Column("order_by", sa.String(), nullable=True),
        sa.Column("auction_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="pwsi",
    )
    op.create_table(
        "credits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("picture", sa.String(), nullable=True),
        sa.Column("picture_size", sa.String(), nullable=True),
        sa.Column("picture_original", sa.String(), nullable=True),
        sa.Column("creators", sa.JSON(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="pwsi",
    )

    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE pwsi.twitchbot_lists SET category = 'save_choices' WHERE category = 'saves';"
        )
    )

    op.add_column(
        "marathons",
        sa.Column("rules", sa.JSON(), nullable=True),
        schema="pwsi",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("credits", schema="pwsi")
    op.drop_table("auctions", schema="pwsi")

    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE pwsi.twitchbot_lists SET category = 'saves' WHERE category = 'save_choices';"
        )
    )

    op.drop_column("marathons", "rules", schema="pwsi")
    # ### end Alembic commands ###
