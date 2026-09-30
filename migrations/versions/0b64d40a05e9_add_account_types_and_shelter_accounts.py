"""Add account types and shelter accounts

Revision ID: 0b64d40a05e9
Revises:
Create Date: 2026-09-30 17:30:03.549707
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b64d40a05e9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add user_id to shelters so a shelter profile can belong
    # to one logged-in PawMatch user.
    with op.batch_alter_table('shelters', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'user_id',
                sa.Integer(),
                nullable=True
            )
        )

        batch_op.create_unique_constraint(
            'uq_shelters_user_id',
            ['user_id']
        )

        batch_op.create_foreign_key(
            'fk_shelters_user_id_users',
            'users',
            ['user_id'],
            ['id']
        )

    # First add account_type as nullable so existing users
    # don't violate a NOT NULL constraint.
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'account_type',
                sa.String(length=20),
                nullable=True
            )
        )

    # Existing PawMatch accounts were created as individuals,
    # so give all existing users that account type.
    op.execute(
        "UPDATE users "
        "SET account_type = 'individual' "
        "WHERE account_type IS NULL"
    )

    # Now that every row has a value, make the column required.
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'account_type',
            existing_type=sa.String(length=20),
            nullable=False
        )


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('account_type')

    with op.batch_alter_table('shelters', schema=None) as batch_op:
        batch_op.drop_constraint(
            'fk_shelters_user_id_users',
            type_='foreignkey'
        )

        batch_op.drop_constraint(
            'uq_shelters_user_id',
            type_='unique'
        )

        batch_op.drop_column('user_id')