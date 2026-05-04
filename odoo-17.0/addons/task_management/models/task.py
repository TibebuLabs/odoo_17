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
