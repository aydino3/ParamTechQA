"""add_subjects_and_teacher_profiles

Revision ID: 292e5554f234
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '292e5554f234'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Subjects table
    op.create_table(
        'subjects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subjects_id'), 'subjects', ['id'], unique=False)
    op.create_index(op.f('ix_subjects_name'), 'subjects', ['name'], unique=True)
    
    # Teacher profiles table
    op.create_table(
        'teacher_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_teacher_profiles_id'), 'teacher_profiles', ['id'], unique=False)
    op.create_index(op.f('ix_teacher_profiles_user_id'), 'teacher_profiles', ['user_id'], unique=True)
    
    # Teacher subjects association table
    op.create_table(
        'teacher_subjects',
        sa.Column('teacher_id', sa.Integer(), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['teacher_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('teacher_id', 'subject_id')
    )


def downgrade() -> None:
    op.drop_table('teacher_subjects')
    op.drop_index(op.f('ix_teacher_profiles_user_id'), table_name='teacher_profiles')
    op.drop_index(op.f('ix_teacher_profiles_id'), table_name='teacher_profiles')
    op.drop_table('teacher_profiles')
    op.drop_index(op.f('ix_subjects_name'), table_name='subjects')
    op.drop_index(op.f('ix_subjects_id'), table_name='subjects')
    op.drop_table('subjects')
