"""Run this script once to write all task_management module files to disk."""
import os

BASE = os.path.dirname(os.path.abspath(__file__))

files = {}

files['__init__.py'] = "from . import models\n"

files['__manifest__.py'] = """\
{
    'name': 'Task Management',
    'version': '17.0.1.0.0',
    'summary': 'Simple and beautiful task management',
    'category': 'Productivity',
    'author': 'Tibebu IT',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/task_views.xml',
        'views/task_menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
"""

files['models/__init__.py'] = "from . import task\n"

files['models/task.py'] = """\
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class TaskTag(models.Model):
    _name = 'task.tag'
    _description = 'Task Tag'

    name = fields.Char(string='Tag', required=True)
    color = fields.Integer(string='Color Index')


class Task(models.Model):
    _name = 'task.task'
    _description = 'Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, deadline asc, id desc'

    name = fields.Char(string='Task Title', required=True, tracking=True)
    description = fields.Html(string='Description')

    stage = fields.Selection([
        ('draft',       'To Do'),
        ('in_progress', 'In Progress'),
        ('review',      'In Review'),
        ('done',        'Done'),
        ('cancelled',   'Cancelled'),
    ], string='Stage', default='draft', tracking=True, group_expand='_expand_stages')

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
        ('2', 'Urgent'),
    ], string='Priority', default='0', tracking=True)

    color = fields.Integer(string='Color', compute='_compute_color')

    assigned_to = fields.Many2one('res.users', string='Assigned To',
                                  default=lambda self: self.env.user, tracking=True)
    reviewer_id = fields.Many2one('res.users', string='Reviewer')
    tag_ids = fields.Many2many('task.tag', string='Tags')

    deadline = fields.Date(string='Deadline', tracking=True)
    date_start = fields.Date(string='Start Date', default=fields.Date.today)
    date_done = fields.Date(string='Completion Date')

    is_overdue = fields.Boolean(string='Overdue', compute='_compute_is_overdue', store=True)
    progress = fields.Integer(string='Progress (%)', default=0)

    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    @api.depends('deadline', 'stage')
    def _compute_is_overdue(self):
        today = date.today()
        for task in self:
            task.is_overdue = (
                bool(task.deadline) and
                task.deadline < today and
                task.stage not in ('done', 'cancelled')
            )

    @api.depends('priority', 'is_overdue')
    def _compute_color(self):
        for task in self:
            if task.is_overdue:
                task.color = 1
            elif task.priority == '2':
                task.color = 2
            elif task.priority == '1':
                task.color = 3
            else:
                task.color = 0

    @api.model
    def _expand_stages(self, states, domain, order):
        return ['draft', 'in_progress', 'review', 'done', 'cancelled']

    @api.constrains('progress')
    def _check_progress(self):
        for task in self:
            if not (0 <= task.progress <= 100):
                raise ValidationError('Progress must be between 0 and 100.')

    @api.constrains('date_start', 'deadline')
    def _check_dates(self):
        for task in self:
            if task.date_start and task.deadline and task.date_start > task.deadline:
                raise ValidationError('Start date cannot be after the deadline.')

    def action_start(self):
        self.write({'stage': 'in_progress', 'date_start': fields.Date.today()})

    def action_review(self):
        self.write({'stage': 'review'})

    def action_done(self):
        self.write({'stage': 'done', 'progress': 100, 'date_done': fields.Date.today()})

    def action_cancel(self):
        self.write({'stage': 'cancelled'})

    def action_reset(self):
        self.write({'stage': 'draft', 'progress': 0, 'date_done': False})
"""

files['security/ir.model.access.csv'] = """\
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_task_task_user,task.task user,model_task_task,,1,1,1,1
access_task_tag_user,task.tag user,model_task_tag,,1,1,1,1
"""

files['views/task_views.xml'] = """\
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <!-- FORM VIEW -->
    <record id="view_task_form" model="ir.ui.view">
        <field name="name">task.task.form</field>
        <field name="model">task.task</field>
        <field name="arch" type="xml">
            <form string="Task">
                <header>
                    <button name="action_start" string="Start" type="object"
                            class="btn-primary"
                            invisible="stage not in ('draft',)"/>
                    <button name="action_review" string="Send to Review" type="object"
                            class="btn-primary"
                            invisible="stage not in ('in_progress',)"/>
                    <button name="action_done" string="Mark Done" type="object"
                            class="btn-success"
                            invisible="stage not in ('in_progress','review')"/>
                    <button name="action_cancel" string="Cancel" type="object"
                            class="btn-danger"
                            invisible="stage in ('done','cancelled')"/>
                    <button name="action_reset" string="Reset" type="object"
                            invisible="stage not in ('cancelled','done')"/>
                    <field name="stage" widget="statusbar"
                           statusbar_visible="draft,in_progress,review,done"/>
                </header>
                <sheet>
                    <div class="oe_button_box" name="button_box"/>
                    <div class="oe_title">
                        <field name="priority" widget="priority" class="me-2"/>
                        <span class="badge bg-danger ms-2" invisible="not is_overdue">Overdue</span>
                        <h1><field name="name" placeholder="Task title..."/></h1>
                    </div>
                    <group>
                        <group string="Assignment">
                            <field name="assigned_to"/>
                            <field name="reviewer_id"/>
                            <field name="tag_ids" widget="many2many_tags"
                                   options="{'color_field': 'color'}"/>
                        </group>
                        <group string="Schedule">
                            <field name="date_start"/>
                            <field name="deadline"/>
                            <field name="date_done" readonly="1"/>
                            <field name="is_overdue" invisible="1"/>
                        </group>
                    </group>
                    <group string="Progress">
                        <field name="progress" widget="progressbar"/>
                    </group>
                    <notebook>
                        <page string="Description">
                            <field name="description" placeholder="Add a description..."/>
                        </page>
                    </notebook>
                </sheet>
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>

    <!-- LIST VIEW -->
    <record id="view_task_list" model="ir.ui.view">
        <field name="name">task.task.tree</field>
        <field name="model">task.task</field>
        <field name="arch" type="xml">
            <tree string="Tasks"
                  decoration-danger="is_overdue == True"
                  decoration-muted="stage == 'cancelled'"
                  decoration-success="stage == 'done'">
                <field name="priority" widget="priority"/>
                <field name="name"/>
                <field name="stage"/>
                <field name="assigned_to" widget="many2one_avatar_user"/>
                <field name="tag_ids" widget="many2many_tags"
                       options="{'color_field': 'color'}"/>
                <field name="deadline"/>
                <field name="progress" widget="progressbar"/>
                <field name="is_overdue" invisible="1"/>
            </tree>
        </field>
    </record>

    <!-- KANBAN VIEW -->
    <record id="view_task_kanban" model="ir.ui.view">
        <field name="name">task.task.kanban</field>
        <field name="model">task.task</field>
        <field name="arch" type="xml">
            <kanban default_group_by="stage" group_create="false" quick_create="false">
                <field name="name"/>
                <field name="stage"/>
                <field name="priority"/>
                <field name="assigned_to"/>
                <field name="deadline"/>
                <field name="is_overdue"/>
                <field name="color"/>
                <field name="tag_ids"/>
                <field name="progress"/>
                <templates>
                    <t t-name="kanban-card">
                        <div class="oe_kanban_card oe_kanban_global_click">
                            <div class="oe_kanban_content">
                                <div class="d-flex justify-content-between align-items-center mb-1">
                                    <field name="priority" widget="priority"/>
                                    <span t-if="record.is_overdue.raw_value"
                                          class="badge bg-danger">Overdue</span>
                                </div>
                                <strong><field name="name"/></strong>
                                <div class="mt-1">
                                    <field name="tag_ids" widget="many2many_tags"
                                           options="{'color_field': 'color'}"/>
                                </div>
                                <div class="d-flex justify-content-between align-items-center mt-2">
                                    <span t-if="record.deadline.raw_value" class="text-muted small">
                                        <field name="deadline"/>
                                    </span>
                                    <field name="assigned_to" widget="many2one_avatar_user"/>
                                </div>
                                <div class="mt-1">
                                    <field name="progress" widget="progressbar"/>
                                </div>
                            </div>
                        </div>
                    </t>
                </templates>
            </kanban>
        </field>
    </record>

    <!-- SEARCH VIEW -->
    <record id="view_task_search" model="ir.ui.view">
        <field name="name">task.task.search</field>
        <field name="model">task.task</field>
        <field name="arch" type="xml">
            <search string="Search Tasks">
                <field name="name" string="Task"/>
                <field name="assigned_to"/>
                <field name="tag_ids"/>
                <filter string="My Tasks" name="my_tasks"
                        domain="[('assigned_to','=',uid)]"/>
                <filter string="Overdue" name="overdue"
                        domain="[('is_overdue','=',True)]"/>
                <filter string="Urgent" name="urgent"
                        domain="[('priority','=','2')]"/>
                <separator/>
                <filter string="To Do" name="todo"
                        domain="[('stage','=','draft')]"/>
                <filter string="In Progress" name="in_progress"
                        domain="[('stage','=','in_progress')]"/>
                <filter string="Done" name="done"
                        domain="[('stage','=','done')]"/>
                <group expand="0" string="Group By">
                    <filter string="Stage" name="group_stage"
                            context="{'group_by': 'stage'}"/>
                    <filter string="Priority" name="group_priority"
                            context="{'group_by': 'priority'}"/>
                    <filter string="Assigned To" name="group_assigned"
                            context="{'group_by': 'assigned_to'}"/>
                    <filter string="Deadline" name="group_deadline"
                            context="{'group_by': 'deadline:month'}"/>
                </group>
            </search>
        </field>
    </record>

    <!-- ACTION -->
    <record id="action_task_task" model="ir.actions.act_window">
        <field name="name">Tasks</field>
        <field name="res_model">task.task</field>
        <field name="view_mode">kanban,tree,form</field>
        <field name="search_view_id" ref="view_task_search"/>
        <field name="context">{'search_default_my_tasks': 1}</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                No tasks yet - create your first one!
            </p>
        </field>
    </record>

    <!-- TAG ACTION -->
    <record id="action_task_tag" model="ir.actions.act_window">
        <field name="name">Tags</field>
        <field name="res_model">task.tag</field>
        <field name="view_mode">list,form</field>
    </record>

</odoo>
"""

files['views/task_menu.xml'] = """\
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <menuitem id="menu_task_root"
              name="Tasks"
              sequence="10"/>

    <menuitem id="menu_task_main"
              name="My Tasks"
              parent="menu_task_root"
              action="action_task_task"
              sequence="1"/>

    <menuitem id="menu_task_config"
              name="Configuration"
              parent="menu_task_root"
              sequence="99"/>

    <menuitem id="menu_task_tags"
              name="Tags"
              parent="menu_task_config"
              action="action_task_tag"
              sequence="1"/>

</odoo>
"""

# Write all files
for rel_path, content in files.items():
    full_path = os.path.join(BASE, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    size = os.path.getsize(full_path)
    print(f"  OK  {rel_path} ({size} bytes)")

print("\nAll files written successfully!")
