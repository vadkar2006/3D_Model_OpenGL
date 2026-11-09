#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <atomic>

#define STB_IMAGE_IMPLEMENTATION
#include "Image/stb_image.h"

#include "NVIDIA/NVIDIA.h"
#include "Shaders/Shader_Compilation.h"
#include "Figure_Conveyor/Figure_Conveyor.h"
#include "Camera/Camera.h"

static int Count_Polygon_Ball = 100;
/*
void mouseButtonCallback(GLFWwindow* window, int button, int action, int mods) {
    if (button == GLFW_MOUSE_BUTTON_1 && (action == GLFW_PRESS || action == GLFW_REPEAT)) zoom /= 1.003;
    if (button == GLFW_MOUSE_BUTTON_2 && (action == GLFW_PRESS || action == GLFW_REPEAT)) zoom *= 1.003; 
}

void mouse_button_callback(GLFWwindow* window, int button, int action, int mods) {
    if (button == GLFW_MOUSE_BUTTON_LEFT && action == GLFW_PRESS) {
        std::cout << "Левая кнопка мыши нажата (например, выстрел)" << std::endl;
    }
    if (button == GLFW_MOUSE_BUTTON_RIGHT && action == GLFW_PRESS) {
        std::cout << "Правая кнопка мыши нажата (например, прицеливание)" << std::endl;
    }
}

// 3. Колесико прокрутки (для зума или смены оружия)
void scroll_callback(GLFWwindow* window, double xoffset, double yoffset) {
    // yoffset обычно равен 1.0 (вверх) или -1.0 (вниз) за один щелчок
    std::cout << "Прокрутка: " << yoffset << std::endl;
    // Например: camera.ProcessMouseScroll(yoffset);
}*/


GLuint Create_Texture(const char file[]){
    //Загружаем картинку
    int width, height, channels;
    unsigned char* data = stbi_load(file, &width, &height, &channels, 0);

    if(!data)
        std::cout << "Текстура не загружена" << std::endl;

    //Создаём текстуру
    GLuint texture;
    glGenTextures(1, &texture);
    glBindTexture(GL_TEXTURE_2D, texture);

    //Настраиваем параметры
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);

    //Загружаем пиксели
    if (channels == 4)
    {
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            width,
            height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            data
        );
    }
    else if (channels == 3)
    {
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGB,
            width,
            height,
            0,
            GL_RGB,
            GL_UNSIGNED_BYTE,
            data
        );
    }

    //Освобождаем данные
    stbi_image_free(data);

    return texture;
}

Camera camera;

int main(){
    // Vertices: 748400, normals: 1496910, texture coordinates: 0, faces: 1497226
    Figure My_Model("../src/Texture/model.obj", 0.1);
    Figure My_Model1("../src/Texture/model.obj");






    // Фигурный конвеер
    Figure_Conveyor fig_con;
    fig_con.Push_Figure(&My_Model);
    fig_con.Push_Figure(&My_Model1);





    fig_con.Preparation_To_VideoCard();
    fig_con.Go_To_VideoCard();




    

    double lastTime = glfwGetTime();
    int frameCount = 0;
    int total_step = 0;
    while (!glfwWindowShouldClose(camera.Get_Window())) {
        //Обработка камеры
        camera.Step_Frame(fig_con);


        //Подсчет FPS
        frameCount++;
        double currentTime = glfwGetTime();
        if (currentTime - lastTime >= 5.0) {
            double fps = frameCount / (currentTime - lastTime);
            
            std::cout << "FPS: " << fps << std::endl;

            frameCount = 0;
            lastTime = currentTime;
        }
        

        glfwPollEvents();
    }


    glfwTerminate();
    return 0;
}