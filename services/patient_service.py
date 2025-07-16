from datetime import date
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import pymysql
import pymysql.cursors
from db.db_mysql import get_db_connection
from models.patient_model import Patient

class Patient_Service:
    def __init__(self):
        self.con=get_db_connection()
        if self.con is None:
            print("No se ha podido establecer conexión con la BD")

    async def get_patients(self):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM paciente")
                users=cursor.fetchall()

                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "Pacientes encontrados",
                        "data": jsonable_encoder(users) if users else []
                    }
                )
        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al consultar pacientes {str(e)} ",
                        "data": None
                    }
                )
        
    async def get_patient_by_id(self, user_id):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql="SELECT * FROM paciente WHERE id_paciente = %s"
                cursor.execute(sql, (user_id,))
                user=cursor.fetchone()

                if user:
                    return JSONResponse(
                        status_code=200,
                        content={
                            "success": True,
                            "message": "Paciente encontrado",
                            "data": jsonable_encoder(user)
                        }
                )
                else:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "success": True,
                            "message": "Paciente no encontrado",
                            "data": None
                        }
                )

        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al consultar el paciente {str(e)} ",
                        "data": None
                    }
                )
        
    async def create_patient(self, user_data: Patient):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                dup="SELECT COUNT(*) FROM paciente WHERE num_docum = %s"
                cursor.execute(dup, (user_data.num_docum,))
                result=cursor.fetchone()

                if result[0] > 0:
                    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "Paciente ya se encuentra registrado",
                            "data": None
                        }
                )

                if (user_data.tipo_docum.lower() == "cédula" and (date.today().year - user_data.fecha_nacim.year) < 18):
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "Paciente no es mayor de edad, por favor elegir otro tipo de documento"
                        }
                    )

                sql='''INSERT INTO paciente (tipo_docum, num_docum, nombre, genero, fecha_nacim, num_celular)
                VALUES ( %s, %s, %s, %s, %s, %s)'''
                cursor.execute(sql, (user_data.tipo_docum, user_data.num_docum, user_data.nombre, user_data.genero, user_data.fecha_nacim, user_data.num_celular))
                self.con.commit()

                if cursor.rowcount > 0:
                     
                    return JSONResponse(
                        status_code=201,
                        content={
                            "success": True,
                            "message": "Se registró el paciente con éxito",
                            "data": {"user_id" : cursor.lastrowid}
                        }
                )

                else:    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "No se pudo registrar el paciente",
                            "data": None
                        }
                )

        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al registrar el paciente {str(e)} ",
                        "data": None
                    }
                )
        
    async def update_patient(self, user_id: int, user_data: Patient):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM paciente WHERE id_paciente=%s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(content={"success": False, "message": "Paciente no encontrado."}, status_code=404)
                
                if (user_data.tipo_docum.lower() == "cédula" and (date.today().year - user_data.fecha_nacim.year) < 18):
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "Paciente no es mayor de edad, por favor elegir otro tipo de documento"
                        }
                    )

                update_sql = """
                    UPDATE paciente
                    SET tipo_docum=%s, num_docum=%s, nombre=%s, genero=%s, fecha_nacim=%s, num_celular=%s
                    WHERE id_paciente=%s
                """
                cursor.execute(update_sql, (
                    user_data.tipo_docum,
                    user_data.num_docum,
                    user_data.nombre,
                    user_data.genero,
                    user_data.fecha_nacim,
                    user_data.num_celular,
                    user_id
                ))

                self.con.commit()

                if cursor.rowcount > 0:
                    return JSONResponse(content={"success": True, "message": "Paciente actualizado correctamente."}, status_code=200)
                else:
                    return JSONResponse(content={"success": False, "message": "No se realizaron cambios."}, status_code=409)

        except Exception as e:
            self.con.rollback()
            return JSONResponse(content={"success": False, "message": f"Error al actualizar paciente: {str(e)}"}, status_code=500)
        
    async def delete_patient(self, user_id):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM paciente WHERE id_paciente=%s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(content={"success": False, "message": "Paciente no encontrado."}, status_code=404)
                
                delete_sql = "DELETE FROM paciente WHERE id_paciente=%s"
                cursor.execute(delete_sql, (user_id))

                self.con.commit()

                return JSONResponse(
                    content={"success": True, "message": "Paciente eliminado"},
                    status_code=200
                )

        except Exception as e:
            self.con.rollback()
            return JSONResponse(content={"success": False, "message": f"Error al eliminar paciente: {str(e)}"}, status_code=500)    