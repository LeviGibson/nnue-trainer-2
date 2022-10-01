#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#define MAX_LINE_LENGTH 100
#define WHITE 1
#define BLACK 0

int getLineCount(FILE *fp){
    int count = 0;
    char c;
    for (c = getc(fp); c != EOF; c = getc(fp))
        if (c == '\n') // Increment count if this character is newline
            count = count + 1;
    fseek(fp, 0L, SEEK_SET);
    return count;
}

char *data;

unsigned char pieces[12][64];
int side;

void init(int val){
    FILE *fin = fopen("chessData.csv", "r");

    int count = getLineCount(fin);
    int lineIndex = 0;
    // char data[count][100];
    data = malloc(sizeof(char) * count * MAX_LINE_LENGTH);

    char c;
    int cindex = 0;

    for (c = getc(fin); c != EOF; c = getc(fin)){
        data[(lineIndex*100) + cindex] = c;
        cindex++;
        if (c == '\n'){
            data[(lineIndex*100) + cindex - 1] = '\0';
            lineIndex++;
            cindex = 0;
        }

        assert(cindex < MAX_LINE_LENGTH);
    }

    fclose(fin);

    for (int i = 0; i < 1000; i+=100) {
        printf("%s\n", &data[i]);
    }
    
}

#ifdef EXE
int main(){

    init(0);

    return 0;
}
#endif
