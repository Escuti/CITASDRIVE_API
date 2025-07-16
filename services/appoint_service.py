from datetime import date
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import pymysql
import pymysql.cursors
from db.db_mysql import get_db_connection
from models.appoint_model import Appoint

class Appoint_Service:
    def __init__(self):
        self.con=get_db_connection()
        if self.con is None:
            print("No se ha podido establecer conexión con la BD")

    async def get_appoints(self):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                    SELECT id_cita, fecha_cita,
                        TIME_FORMAT(hora_inicio, '%H:%i') AS hora_inicio,
                        TIME_FORMAT(hora_fin, '%H:%i') AS hora_fin,
                        doc_asig, pacienteFK
                    FROM citas
                """)
                appoints=cursor.fetchall()

                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "Citas desplegadas",
                        "data": jsonable_encoder(appoints) if appoints else []
                    }
                )
        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al consultar citas {str(e)} ",
                        "data": None
                    }
                )
        
    async def get_appoint_by_patient(self, patient_id):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql="SELECT * FROM citas WHERE pacienteFK = %s"
                cursor.execute(sql, (patient_id,))
                appoints=cursor.fetchone()

                if appoints:
                    return JSONResponse(
                        status_code=200,
                        content={
                            "success": True,
                            "message": "Cita desplegada",
                            "data": jsonable_encoder(appoints)
                        }
                )
                else:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "success": True,
                            "message": "Cita no encontrada",
                            "data": None
                        }
                )

        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al consultar la cita {str(e)} ",
                        "data": None
                    }
                )
        
    async def create_appoint(self, appoint_data: Appoint):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                hora_inicio_str = appoint_data.hora_inicio.strftime("%H:%M:%S")
                hora_fin_str = appoint_data.hora_fin.strftime("%H:%M:%S")

                print(hora_inicio_str, hora_fin_str)
                
                dup = "SELECT COUNT(*) FROM citas WHERE fecha_cita=%s AND hora_inicio=%s AND doc_asig=%s"
                cursor.execute(dup, (appoint_data.fecha_cita, hora_inicio_str, appoint_data.doc_asig))
                
                if cursor.fetchone()[0] > 0:
                    return JSONResponse(
                        status_code=400, 
                        content={"success": False, 
                                 "message": "Cita ya existe"})
                
                dupday = "SELECT COUNT(*) FROM citas WHERE fecha_cita=%s AND pacienteFK=%s"
                cursor.execute(dupday, (appoint_data.fecha_cita, appoint_data.pacienteFK))
                
                if cursor.fetchone()[0] > 0:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "El paciente ya tiene una cita para la fecha indicada"
                        }
                    )

                min_inicio = appoint_data.hora_inicio.hour * 60 + appoint_data.hora_inicio.minute
                min_fin = appoint_data.hora_fin.hour * 60 + appoint_data.hora_fin.minute
                tiempo = min_fin - min_inicio

                if min_fin <= min_inicio:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "message": "hora_fin debe ser mayor a hora_inicio"}
                    )

                elif (tiempo > 60):
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "La duración de la cita no puede ser superior a 60 minutos"
                        }
                    )
                
                elif (appoint_data.fecha_cita < date.today()):
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "No puede seleccionar una fecha anterior a hoy"
                        }
                    )
                
                sql = """INSERT INTO citas 
                    (fecha_cita, hora_inicio, hora_fin, doc_asig, pacienteFK)
                    VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql, (
                    appoint_data.fecha_cita,
                    hora_inicio_str,
                    hora_fin_str,
                    appoint_data.doc_asig,
                    appoint_data.pacienteFK
                ))
                self.con.commit()

                if cursor.rowcount > 0:
                    return JSONResponse(content={"success": True, "message": "Cita agendada."}, status_code=200)
                else:
                    return JSONResponse(content={"success": False, "message": "No se pudo agendar la cita."}, status_code=409)
                
        except Exception as e:
            self.con.rollback()
            return JSONResponse(status_code=500, content={"success": False, "message": f"Error al agendar cita: {str(e)}"})
        
    async def update_appoint(self, appoint_id: int, appoint_data: Appoint):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM citas WHERE id_cita=%s", (appoint_id,))
                if cursor.fetchone()[0] == 0:
                    return JSONResponse(
                        content={"success": False, "message": "Cita no encontrada"},
                        status_code=404
                    )

                dup = """SELECT COUNT(*) FROM citas WHERE fecha_cita=%s AND hora_inicio=%s AND doc_asig=%s"""
                cursor.execute(dup, (appoint_data.fecha_cita, appoint_data.hora_inicio, appoint_data.doc_asig))
                
                if cursor.fetchone()[0] > 0:
                    return JSONResponse(
                        status_code=400, 
                        content={"success": False, 
                                 "message": "Cita ya existe"})

                min_inicio = appoint_data.hora_inicio.hour * 60 + appoint_data.hora_inicio.minute
                min_fin = appoint_data.hora_fin.hour * 60 + appoint_data.hora_fin.minute
                tiempo = min_fin - min_inicio

                if min_fin <= min_inicio:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "message": "hora_fin debe ser mayor a hora_inicio"}
                    )

                elif (tiempo > 60):
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "La duración de la cita no puede ser superior a 60 minutos"
                        }
                    )
                
                elif (appoint_data.fecha_cita < date.today()):
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "No puede seleccionar una fecha anterior a hoy"
                        }
                    )

                cursor.execute(
                    """UPDATE citas 
                    SET fecha_cita=%s, hora_inicio=%s, hora_fin=%s, 
                        doc_asig=%s, pacienteFK=%s 
                    WHERE id_cita=%s""",
                    (
                        appoint_data.fecha_cita,
                        appoint_data.hora_inicio.strftime("%H:%M:%S"),
                        appoint_data.hora_fin.strftime("%H:%M:%S"),
                        appoint_data.doc_asig,
                        appoint_data.pacienteFK,
                        appoint_id
                    )
                )
                self.con.commit()

                return JSONResponse(
                    content={"success": True, "message": "Cita actualizada"},
                    status_code=200
                )

        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                content={"success": False, "message": f"Error: {str(e)}"},
                status_code=500
            )
        
    async def delete_appoint(self, appoint_id):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM citas WHERE id_cita=%s"
                cursor.execute(sql, (appoint_id,))
                result = cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(content={"success": False, "message": "Cita no encontrada."}, status_code=404)
                
                delete_sql = "DELETE FROM citas WHERE id_cita=%s"
                cursor.execute(delete_sql, (appoint_id))

                self.con.commit()

                return JSONResponse(
                    content={"success": True, "message": "Cita cancelada"},
                    status_code=200
                )

        except Exception as e:
            self.con.rollback()
            return JSONResponse(content={"success": False, "message": f"Error al cancelar la cita: {str(e)}"}, status_code=500)    