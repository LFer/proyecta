# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from openerp import api, SUPERUSER_ID
import ipdb
import time
import datetime
import uuid
_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    start_time = time.time()
    env = api.Environment(cr, SUPERUSER_ID, {})
    task_obj = env['project.task']
    tasks = task_obj.search([], order='id')
    total = len(tasks)
    contador = 1
    for task in tasks:
        access_token = uuid.uuid4().hex
        task.access_token = access_token
        _logger.info('creating access token %s for task %s %s/%s' %(access_token, task.name, str(contador), str(total)))
        contador += 1
    end_time = time.time()
    time_passed = round(end_time - start_time)
    cantidad_viajes_creados = total
    tiempo_transcurrido_en_segundos = datetime.timedelta(seconds=time_passed)
    cantidad_entre_tiempo = round(tiempo_transcurrido_en_segundos.seconds / cantidad_viajes_creados if cantidad_viajes_creados else 1, 2)
    body = "%s registros actualizados en %s eso es un promedio de %s por registro" % (cantidad_viajes_creados, tiempo_transcurrido_en_segundos, cantidad_entre_tiempo)
    print(body)